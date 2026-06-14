from __future__ import annotations

from delivery_ops.application.intent_router import IntentRouter
from delivery_ops.application.report_publisher import ReportPublisher
from delivery_ops.application.system_handler import SystemHandler
from delivery_ops.application.workflow_router import WorkflowRouter
from delivery_ops.domain.intents import TaskIntent, WorkflowType
from delivery_ops.domain.messages import NormalizedMessage
from delivery_ops.domain.reports import AgentReport
from delivery_ops.graphs.bugfix.graph import BugFixGraph
from delivery_ops.graphs.feature.graph import FeatureGraph


class IngressService:
    """入口用例服务：分类意图 → 路由工作流 → 分发 Graph → 发布报告。"""

    def __init__(
        self,
        intent_router: IntentRouter,
        workflow_router: WorkflowRouter,
        bugfix_graph: BugFixGraph,
        feature_graph: FeatureGraph,
        system_handler: SystemHandler,
        report_publisher: ReportPublisher,
    ) -> None:
        self._intent_router = intent_router
        self._workflow_router = workflow_router
        self._bugfix_graph = bugfix_graph
        self._feature_graph = feature_graph
        self._system_handler = system_handler
        self._report_publisher = report_publisher

    async def handle_message(self, message: NormalizedMessage) -> AgentReport:
        intent = self._intent_router.classify(message.text)
        if intent == TaskIntent.UNKNOWN:
            return self._report_publisher.build_unknown(intent)

        workflow = self._workflow_router.resolve(intent)
        if workflow == WorkflowType.BUG_FIX:
            snapshot, bugfix_state = await self._bugfix_graph.run(intent, message)
            return self._report_publisher.build(
                snapshot,
                intent,
                bugfix=bugfix_state.to_artifacts(),
                error=bugfix_state.error,
            )
        if workflow == WorkflowType.FEATURE_DEVELOPMENT:
            snapshot, feature_state = await self._feature_graph.run(intent, message)
            return self._report_publisher.build(
                snapshot,
                intent,
                feature=feature_state.to_artifacts(),
                error=feature_state.error,
            )

        snapshot = await self._system_handler.handle(intent, message)
        return self._report_publisher.build(snapshot, intent)
