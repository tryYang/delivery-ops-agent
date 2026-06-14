from __future__ import annotations

from delivery_ops.domain.intents import TaskIntent, WorkflowType


class WorkflowRouter:
    """将 TaskIntent 映射到隔离的工作流；unknown 归入 system 元操作。"""

    _BUG_INTENTS: frozenset[TaskIntent] = frozenset(
        {
            TaskIntent.LIST_SERIOUS_BUGS,
            TaskIntent.ANALYZE_BUG,
            TaskIntent.GENERATE_FIX_ORDER,
        }
    )

    _FEATURE_INTENTS: frozenset[TaskIntent] = frozenset(
        {
            TaskIntent.LIST_FEATURE_TASKS,
            TaskIntent.ANALYZE_FEATURE,
            TaskIntent.GENERATE_FEATURE_ORDER,
        }
    )

    _SYSTEM_INTENTS: frozenset[TaskIntent] = frozenset(
        {
            TaskIntent.TASK_STATUS,
            TaskIntent.CANCEL_TASK,
            TaskIntent.UNKNOWN,
        }
    )

    def resolve(self, intent: TaskIntent) -> WorkflowType:
        if intent in self._BUG_INTENTS:
            return WorkflowType.BUG_FIX
        if intent in self._FEATURE_INTENTS:
            return WorkflowType.FEATURE_DEVELOPMENT
        if intent in self._SYSTEM_INTENTS:
            return WorkflowType.SYSTEM
        # 防御性兜底：未登记意图仍走 system，不误入交付 Graph。
        return WorkflowType.SYSTEM
