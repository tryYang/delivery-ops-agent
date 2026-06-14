from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from delivery_ops.application.bugfix.bug_ref_parser import BugRefParseError, BugRefParser
from delivery_ops.application.bugfix.bug_severity_ranker import BugSeverityRanker
from delivery_ops.application.evidence.bug_evidence_builder import BugEvidenceBuilder
from delivery_ops.application.risk.bug_risk_judge import BugRiskJudge
from delivery_ops.application.work_orders.fix_work_order_compiler import FixWorkOrderCompiler
from delivery_ops.domain.bugfix import BugRiskAssessment, RankedBug
from delivery_ops.domain.intents import TaskIntent, WorkflowType
from delivery_ops.domain.messages import NormalizedMessage
from delivery_ops.domain.ports import BugSourceAdapter, PrdResolverPort, RepoSearchPort
from delivery_ops.domain.tasks import TaskEvent, TaskSnapshot, TaskStatus
from delivery_ops.graphs.bugfix.state import BugFixState
from delivery_ops.storage.in_memory_bug_fix_session import InMemoryBugFixSession
from delivery_ops.storage.in_memory_task_store import InMemoryTaskStore


class BugFixGraph:
    """Bug Fix Python 编排器；Phase 4 可替换为 LangGraph，状态模型保持不变。"""

    def __init__(
        self,
        task_store: InMemoryTaskStore,
        bug_source: BugSourceAdapter,
        prd_resolver: PrdResolverPort,
        repo_search: RepoSearchPort,
        ranker: BugSeverityRanker,
        ref_parser: BugRefParser,
        evidence_builder: BugEvidenceBuilder,
        risk_judge: BugRiskJudge,
        work_order_compiler: FixWorkOrderCompiler,
        session: InMemoryBugFixSession,
    ) -> None:
        self._task_store = task_store
        self._bug_source = bug_source
        self._prd_resolver = prd_resolver
        self._repo_search = repo_search
        self._ranker = ranker
        self._ref_parser = ref_parser
        self._evidence_builder = evidence_builder
        self._risk_judge = risk_judge
        self._work_order_compiler = work_order_compiler
        self._session = session

    async def run(
        self,
        intent: TaskIntent,
        message: NormalizedMessage,
    ) -> tuple[TaskSnapshot, BugFixState]:
        state = BugFixState(intent=intent, message=message)
        snapshot = await self._create_snapshot(message, intent, TaskStatus.ANALYZING)
        state.snapshot = snapshot

        if intent == TaskIntent.LIST_SERIOUS_BUGS:
            await self._run_list_serious_bugs(state, snapshot)
        elif intent == TaskIntent.ANALYZE_BUG:
            await self._run_analyze_bug(state, snapshot, message)
        elif intent == TaskIntent.GENERATE_FIX_ORDER:
            await self._run_generate_fix_order(state, snapshot, message)
        else:
            state.error = f"Unsupported bug fix intent: {intent.value}"

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

    async def _run_list_serious_bugs(self, state: BugFixState, snapshot: TaskSnapshot) -> None:
        bugs = await self._bug_source.list_open_bugs()
        scores = self._ranker.rank_top(bugs, limit=3)
        bug_map = {b.bug_id: b for b in bugs}
        ranked: list[RankedBug] = []
        for score in scores:
            summary = bug_map.get(score.bug_id)
            if summary is None:
                continue
            ranked.append(
                RankedBug(
                    **summary.model_dump(),
                    score=score.score,
                    reasons=score.reasons,
                )
            )
        state.ranked_bugs = ranked
        self._session.save_ranked_bugs(snapshot.user_id, ranked)

    async def _run_analyze_bug(
        self,
        state: BugFixState,
        snapshot: TaskSnapshot,
        message: NormalizedMessage,
    ) -> None:
        ranked = self._session.get_ranked_bugs(message.user_id)
        try:
            bug_id = self._ref_parser.parse(message.text, ranked)
        except BugRefParseError as exc:
            state.error = str(exc)
            return

        state.selected_bug_id = bug_id
        detail = await self._bug_source.get_bug_detail(bug_id)
        if detail is None:
            state.error = f"Bug {bug_id} 不存在。"
            return

        _prd_ref, prd_doc = await self._prd_resolver.resolve(detail)
        code_hits = await self._repo_search.search(detail)
        evidence = await self._evidence_builder.build(detail, prd_doc, code_hits)
        risk = self._risk_judge.assess(detail, evidence)

        state.evidence = evidence
        state.risk = risk
        self._session.save_evidence(evidence)
        self._session.save_risk(bug_id, risk)

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
                payload={"bug_id": bug_id, "risk_level": risk.level.value},
                created_at=datetime.now(UTC),
            )
        )

    async def _run_generate_fix_order(
        self,
        state: BugFixState,
        snapshot: TaskSnapshot,
        message: NormalizedMessage,
    ) -> None:
        ranked = self._session.get_ranked_bugs(message.user_id)
        try:
            bug_id = self._ref_parser.parse(message.text, ranked)
        except BugRefParseError as exc:
            state.error = str(exc)
            return

        evidence = self._session.get_evidence(bug_id)
        if evidence is None:
            state.error = f"Bug {bug_id} 尚无证据包，请先执行分析。"
            return

        stored_risk = self._session.get_risk(bug_id)
        if stored_risk is None:
            state.error = f"Bug {bug_id} 尚无风险评估，请先执行分析。"
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
                payload={"bug_id": bug_id, "risk_level": stored_risk.level.value},
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
            workflow_type=WorkflowType.BUG_FIX,
            intent=intent,
            status=status,
            user_id=message.user_id,
            input_text=message.text,
            created_at=now,
            updated_at=now,
        )
        await self._task_store.create_snapshot(snapshot)
        return snapshot
