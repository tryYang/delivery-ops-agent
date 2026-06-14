from __future__ import annotations

from delivery_ops.domain.intents import TaskIntent


class IntentRouter:
    """Phase 1 规则分类器：稳定可测，不依赖 LLM；Phase 2+ 可替换实现。"""

    # 插入顺序即匹配优先级：Bug → Feature → System，避免宽泛关键词误命中。
    _BUG_KEYWORDS: dict[TaskIntent, tuple[str, ...]] = {
        TaskIntent.LIST_SERIOUS_BUGS: (
            "严重 bug",
            "严重bug",
            "serious bug",
            "critical bug",
            "严重缺陷",
            "有哪些严重 bug",
        ),
        TaskIntent.ANALYZE_BUG: (
            "分析 bug",
            "分析bug",
            "analyze bug",
            "bug 分析",
            "bug分析",
            "分析第",
            "个 bug",
            "个bug",
        ),
        TaskIntent.GENERATE_FIX_ORDER: (
            "修复工单",
            "生成修复",
            "fix order",
            "fix work order",
            "生成修复工单",
        ),
    }

    _FEATURE_KEYWORDS: dict[TaskIntent, tuple[str, ...]] = {
        TaskIntent.LIST_FEATURE_TASKS: (
            "功能任务",
            "feature task",
            "feature tasks",
            "需求列表",
            "新功能",
            "有哪些新功能",
        ),
        TaskIntent.ANALYZE_FEATURE: (
            "分析功能",
            "分析需求",
            "analyze feature",
            "feature 分析",
            "分析新功能",
            "个新功能",
            "个功能",
        ),
        TaskIntent.GENERATE_FEATURE_ORDER: (
            "功能工单",
            "feature order",
            "feature work order",
            "生成功能工单",
            "生成开发工单",
        ),
    }

    _SYSTEM_KEYWORDS: dict[TaskIntent, tuple[str, ...]] = {
        TaskIntent.TASK_STATUS: (
            "任务状态",
            "查看任务",
            "task status",
            "status of task",
        ),
        TaskIntent.CANCEL_TASK: (
            "取消任务",
            "cancel task",
            "终止任务",
            "停止任务",
        ),
    }

    def classify(self, text: str) -> TaskIntent:
        normalized = text.strip().lower()
        for intent, keywords in (
            *self._BUG_KEYWORDS.items(),
            *self._FEATURE_KEYWORDS.items(),
            *self._SYSTEM_KEYWORDS.items(),
        ):
            if any(keyword.lower() in normalized for keyword in keywords):
                return intent
        return TaskIntent.UNKNOWN
