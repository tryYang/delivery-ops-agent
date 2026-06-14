from __future__ import annotations

from delivery_ops.application.intent_router import IntentRouter
from delivery_ops.domain.intents import TaskIntent


class TestIntentRouter:
    def setup_method(self) -> None:
        self.router = IntentRouter()

    def test_list_serious_bugs(self) -> None:
        assert self.router.classify("查看现在有哪些严重 bug") == TaskIntent.LIST_SERIOUS_BUGS

    def test_list_feature_tasks(self) -> None:
        assert self.router.classify("查看当前迭代有哪些新功能") == TaskIntent.LIST_FEATURE_TASKS

    def test_task_status(self) -> None:
        assert self.router.classify("查看任务 #123") == TaskIntent.TASK_STATUS

    def test_analyze_first_new_feature_intent(self) -> None:
        assert self.router.classify("分析第1个新功能") == TaskIntent.ANALYZE_FEATURE

    def test_analyze_first_bug_intent(self) -> None:
        assert self.router.classify("分析第1个bug") == TaskIntent.ANALYZE_BUG

    def test_unknown(self) -> None:
        assert self.router.classify("随便说句话") == TaskIntent.UNKNOWN
