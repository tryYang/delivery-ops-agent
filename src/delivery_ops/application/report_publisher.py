from __future__ import annotations

from delivery_ops.domain.intents import TaskIntent, WorkflowType
from delivery_ops.domain.reports import AgentReport
from delivery_ops.domain.tasks import TaskSnapshot, TaskStatus


class ReportPublisher:
    """将 TaskSnapshot 转为用户可读 AgentReport；Phase 1 仅返回占位文案。"""

    _PLACEHOLDER_MESSAGES: dict[TaskIntent, str] = {
        TaskIntent.LIST_SERIOUS_BUGS: "Bug Fix workflow placeholder ready",
        TaskIntent.ANALYZE_BUG: "Bug analysis started (placeholder).",
        TaskIntent.GENERATE_FIX_ORDER: "Fix work order generation started (placeholder).",
        TaskIntent.LIST_FEATURE_TASKS: "Feature workflow placeholder ready",
        TaskIntent.ANALYZE_FEATURE: "Feature analysis started (placeholder).",
        TaskIntent.GENERATE_FEATURE_ORDER: "Feature work order generation started (placeholder).",
        TaskIntent.TASK_STATUS: "Task status retrieved (placeholder).",
        TaskIntent.CANCEL_TASK: "Task cancellation processed (placeholder).",
        TaskIntent.UNKNOWN: "Intent not recognized.",
    }

    def build(self, snapshot: TaskSnapshot, intent: TaskIntent) -> AgentReport:
        message = self._PLACEHOLDER_MESSAGES.get(intent, "Request processed (placeholder).")
        return AgentReport(
            task_id=snapshot.task_id,
            workflow_type=snapshot.workflow_type,
            intent=intent,
            status=snapshot.status,
            message=message,
            details={
                "input_text": snapshot.input_text,
                "user_id": snapshot.user_id,
            },
        )

    def build_unknown(self, intent: TaskIntent = TaskIntent.UNKNOWN) -> AgentReport:
        # 无关联任务，task_id 留空，调用方据此判断未创建 TaskSnapshot。
        return AgentReport(
            task_id="",
            workflow_type=WorkflowType.SYSTEM,
            intent=intent,
            status=TaskStatus.CREATED,
            message=self._PLACEHOLDER_MESSAGES[TaskIntent.UNKNOWN],
            details={},
        )
