from __future__ import annotations

from delivery_ops.application.workflow_router import WorkflowRouter
from delivery_ops.domain.intents import TaskIntent, WorkflowType


class TestWorkflowRouter:
    def setup_method(self) -> None:
        self.router = WorkflowRouter()

    def test_bug_intent_routes_to_bug_fix(self) -> None:
        assert self.router.resolve(TaskIntent.ANALYZE_BUG) == WorkflowType.BUG_FIX

    def test_feature_intent_routes_to_feature_development(self) -> None:
        assert self.router.resolve(TaskIntent.LIST_FEATURE_TASKS) == WorkflowType.FEATURE_DEVELOPMENT

    def test_system_intent_routes_to_system(self) -> None:
        assert self.router.resolve(TaskIntent.TASK_STATUS) == WorkflowType.SYSTEM
        assert self.router.resolve(TaskIntent.UNKNOWN) == WorkflowType.SYSTEM
