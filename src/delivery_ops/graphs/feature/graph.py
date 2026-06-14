from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from delivery_ops.application.design.design_context_service import DesignContextService
from delivery_ops.application.evidence.feature_evidence_builder import FeatureEvidenceBuilder
from delivery_ops.application.feature.dependency_mapper import DependencyMapper
from delivery_ops.application.feature.feature_ref_parser import FeatureRefParseError, FeatureRefParser
from delivery_ops.application.feature.feature_readiness_ranker import FeatureReadinessRanker
from delivery_ops.application.prd.feature_prd_analyzer import FeaturePrdAnalyzer
from delivery_ops.application.risk.feature_risk_planner import FeatureRiskPlanner
from delivery_ops.application.work_orders.feature_work_order_compiler import FeatureWorkOrderCompiler
from delivery_ops.domain.features import RankedFeature
from delivery_ops.domain.intents import TaskIntent, WorkflowType
from delivery_ops.domain.messages import NormalizedMessage
from delivery_ops.domain.ports import FeatureRepoSearchPort, RequirementSourceAdapter
from delivery_ops.domain.tasks import TaskEvent, TaskSnapshot, TaskStatus
from delivery_ops.graphs.feature.state import FeatureState
from delivery_ops.storage.in_memory_feature_session import InMemoryFeatureSession
from delivery_ops.storage.in_memory_task_store import InMemoryTaskStore


class FeatureGraph:
    """Feature Development Python 编排器；与 BugFixGraph 隔离，Phase 4 可换 LangGraph。"""

    def __init__(
        self,
        task_store: InMemoryTaskStore,
        requirement_source: RequirementSourceAdapter,
        prd_analyzer: FeaturePrdAnalyzer,
        design_service: DesignContextService,
        repo_search: FeatureRepoSearchPort,
        ranker: FeatureReadinessRanker,
        ref_parser: FeatureRefParser,
        dependency_mapper: DependencyMapper,
        evidence_builder: FeatureEvidenceBuilder,
        risk_planner: FeatureRiskPlanner,
        work_order_compiler: FeatureWorkOrderCompiler,
        session: InMemoryFeatureSession,
    ) -> None:
        self._task_store = task_store
        self._requirement_source = requirement_source
        self._prd_analyzer = prd_analyzer
        self._design_service = design_service
        self._repo_search = repo_search
        self._ranker = ranker
        self._ref_parser = ref_parser
        self._dependency_mapper = dependency_mapper
        self._evidence_builder = evidence_builder
        self._risk_planner = risk_planner
        self._work_order_compiler = work_order_compiler
        self._session = session

    async def run(
        self,
        intent: TaskIntent,
        message: NormalizedMessage,
    ) -> tuple[TaskSnapshot, FeatureState]:
        state = FeatureState(intent=intent, message=message)
        snapshot = await self._create_snapshot(message, intent, TaskStatus.ANALYZING)
        state.snapshot = snapshot

        if intent == TaskIntent.LIST_FEATURE_TASKS:
            await self._run_list_features(state, snapshot)
        elif intent == TaskIntent.ANALYZE_FEATURE:
            await self._run_analyze_feature(state, snapshot, message)
        elif intent == TaskIntent.GENERATE_FEATURE_ORDER:
            await self._run_generate_feature_order(state, snapshot, message)
        else:
            state.error = f"Unsupported feature intent: {intent.value}"

        if state.error:
            updated = snapshot.model_copy(
                update={"status": TaskStatus.FAILED, "updated_at": datetime.now(UTC)}
            )
            await self._task_store.update_snapshot(updated)
            state.snapshot = updated

        return state.snapshot, state

    async def run_placeholder(
        self,
        intent: TaskIntent,
        message: NormalizedMessage,
    ) -> TaskSnapshot:
        snapshot, _ = await self.run(intent, message)
        return snapshot

    async def _run_list_features(self, state: FeatureState, snapshot: TaskSnapshot) -> None:
        features = await self._requirement_source.list_pending_features()
        scores = self._ranker.rank_top(features, limit=3)
        feature_map = {f.feature_id: f for f in features}
        ranked: list[RankedFeature] = []
        for score in scores:
            summary = feature_map.get(score.feature_id)
            if summary is None:
                continue
            ranked.append(
                RankedFeature(
                    **summary.model_dump(),
                    score=score.score,
                    reasons=score.reasons,
                )
            )
        state.ranked_features = ranked
        self._session.save_ranked_features(snapshot.user_id, ranked)

    async def _run_analyze_feature(
        self,
        state: FeatureState,
        snapshot: TaskSnapshot,
        message: NormalizedMessage,
    ) -> None:
        ranked = self._session.get_ranked_features(message.user_id)
        try:
            feature_id = self._ref_parser.parse(message.text, ranked)
        except FeatureRefParseError as exc:
            state.error = str(exc)
            return

        state.selected_feature_id = feature_id
        detail = await self._requirement_source.get_feature_detail(feature_id)
        if detail is None:
            state.error = f"Feature {feature_id} 不存在。"
            return

        prd = await self._prd_analyzer.analyze(detail)
        design = await self._design_service.load(detail)
        code_hits = await self._repo_search.search_reusable(detail)
        dependencies = self._dependency_mapper.map(detail, prd, design)
        evidence = await self._evidence_builder.build(
            detail, prd, design, code_hits, dependencies
        )
        risk = self._risk_planner.assess(detail, evidence, dependencies)

        state.evidence = evidence
        state.risk = risk
        self._session.save_evidence(evidence)
        self._session.save_risk(feature_id, risk)

        updated = snapshot.model_copy(
            update={"status": TaskStatus.WAITING_APPROVAL, "updated_at": datetime.now(UTC)}
        )
        await self._task_store.update_snapshot(updated)
        state.snapshot = updated
        await self._task_store.append_event(
            TaskEvent(
                event_id=uuid4().hex,
                task_id=snapshot.task_id,
                event_type="evidence_built",
                payload={"feature_id": feature_id, "risk_level": risk.level.value},
                created_at=datetime.now(UTC),
            )
        )

    async def _run_generate_feature_order(
        self,
        state: FeatureState,
        snapshot: TaskSnapshot,
        message: NormalizedMessage,
    ) -> None:
        ranked = self._session.get_ranked_features(message.user_id)
        try:
            feature_id = self._ref_parser.parse(message.text, ranked)
        except FeatureRefParseError as exc:
            state.error = str(exc)
            return

        evidence = self._session.get_evidence(feature_id)
        if evidence is None:
            state.error = f"Feature {feature_id} 尚无证据包，请先执行分析。"
            return

        stored_risk = self._session.get_risk(feature_id)
        if stored_risk is None:
            state.error = f"Feature {feature_id} 尚无风险评估，请先执行分析。"
            return

        work_order = await self._work_order_compiler.compile(evidence, stored_risk)
        state.work_order = work_order
        state.evidence = evidence
        state.risk = stored_risk

        updated = snapshot.model_copy(
            update={"status": TaskStatus.WAITING_APPROVAL, "updated_at": datetime.now(UTC)}
        )
        await self._task_store.update_snapshot(updated)
        state.snapshot = updated
        await self._task_store.append_event(
            TaskEvent(
                event_id=uuid4().hex,
                task_id=snapshot.task_id,
                event_type="work_order_compiled",
                payload={"feature_id": feature_id, "risk_level": stored_risk.level.value},
                created_at=datetime.now(UTC),
            )
        )

    async def _create_snapshot(
        self,
        message: NormalizedMessage,
        intent: TaskIntent,
        status: TaskStatus,
    ) -> TaskSnapshot:
        now = datetime.now(UTC)
        snapshot = TaskSnapshot(
            task_id=uuid4().hex,
            workflow_type=WorkflowType.FEATURE_DEVELOPMENT,
            intent=intent,
            status=status,
            user_id=message.user_id,
            input_text=message.text,
            created_at=now,
            updated_at=now,
        )
        await self._task_store.create_snapshot(snapshot)
        return snapshot
