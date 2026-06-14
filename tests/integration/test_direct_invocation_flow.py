from __future__ import annotations

import pytest

from delivery_ops.adapters.ingress.direct_invocation import DirectInvocationIngressAdapter
from delivery_ops.domain.intents import TaskIntent, WorkflowType
from delivery_ops.domain.tasks import TaskStatus


class TestDirectInvocationFlow:
    @pytest.mark.asyncio
    async def test_bug_fix_flow(self, direct_adapter: DirectInvocationIngressAdapter) -> None:
        report = await direct_adapter.invoke("查看现在有哪些严重 bug", user_id="user-1")
        assert report.workflow_type == WorkflowType.BUG_FIX
        assert report.intent == TaskIntent.LIST_SERIOUS_BUGS
        assert report.status == TaskStatus.ANALYZING
        assert report.task_id != ""

    @pytest.mark.asyncio
    async def test_feature_flow(self, direct_adapter: DirectInvocationIngressAdapter) -> None:
        report = await direct_adapter.invoke("查看当前迭代有哪些新功能")
        assert report.workflow_type == WorkflowType.FEATURE_DEVELOPMENT
        assert report.intent == TaskIntent.LIST_FEATURE_TASKS

    @pytest.mark.asyncio
    async def test_system_task_status_flow(
        self, direct_adapter: DirectInvocationIngressAdapter
    ) -> None:
        report = await direct_adapter.invoke("查看任务 #123")
        assert report.workflow_type == WorkflowType.SYSTEM
        assert report.intent == TaskIntent.TASK_STATUS
        assert report.task_id != ""

    @pytest.mark.asyncio
    async def test_unknown_intent(self, direct_adapter: DirectInvocationIngressAdapter) -> None:
        report = await direct_adapter.invoke("随便说句话")
        assert report.intent == TaskIntent.UNKNOWN
        assert report.message == "Intent not recognized."
        assert report.task_id == ""
