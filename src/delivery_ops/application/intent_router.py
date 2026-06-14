from __future__ import annotations

import re

from delivery_ops.domain.intents import TaskIntent

_FEATURE_INDEX_PATTERN = re.compile(r"第\s*\d+\s*个.*(新功能|功能|需求|feature)")
_BUG_INDEX_PATTERN = re.compile(r"第\s*\d+\s*个.*(bug|缺陷)")


class IntentRouter:
    """Phase 1 规则分类器：稳定可测，不依赖 LLM；Phase 2+ 可替换实现。"""

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
        # 「第 N 个」歧义：Feature/Bug 专属模式优先于泛化关键词。
        if _FEATURE_INDEX_PATTERN.search(normalized):
            return TaskIntent.ANALYZE_FEATURE
        if _BUG_INDEX_PATTERN.search(normalized):
            return TaskIntent.ANALYZE_BUG

        for intent, keywords in (
            *self._BUG_KEYWORDS.items(),
            *self._FEATURE_KEYWORDS.items(),
            *self._SYSTEM_KEYWORDS.items(),
        ):
            if any(keyword.lower() in normalized for keyword in keywords):
                return intent
        return TaskIntent.UNKNOWN
