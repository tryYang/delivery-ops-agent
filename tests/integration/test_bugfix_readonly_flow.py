from __future__ import annotations

import pytest

from delivery_ops.adapters.ingress.direct_invocation import DirectInvocationIngressAdapter
from delivery_ops.domain.intents import TaskIntent
from delivery_ops.domain.tasks import TaskStatus
from delivery_ops.storage.in_memory_task_store import InMemoryTaskStore


class TestBugfixReadonlyFlow:
    @pytest.mark.asyncio
    async def test_list_serious_bugs(
        self,
        direct_adapter: DirectInvocationIngressAdapter,
    ) -> None:
        report = await direct_adapter.invoke("查看现在有哪些严重 bug", user_id="alice")
        assert report.intent == TaskIntent.LIST_SERIOUS_BUGS
        assert report.bugfix is not None
        assert report.bugfix.top_bugs is not None
        assert len(report.bugfix.top_bugs) <= 3
        scores = [b.score for b in report.bugfix.top_bugs]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_analyze_first_bug(
        self,
        direct_adapter: DirectInvocationIngressAdapter,
    ) -> None:
        await direct_adapter.invoke("查看现在有哪些严重 bug", user_id="alice")
        report = await direct_adapter.invoke("分析第1个bug", user_id="alice")
        assert report.intent == TaskIntent.ANALYZE_BUG
        assert report.bugfix is not None
        assert report.bugfix.evidence is not None
        assert report.bugfix.risk is not None
        assert report.status == TaskStatus.WAITING_APPROVAL

    @pytest.mark.asyncio
    async def test_generate_fix_order(
        self,
        direct_adapter: DirectInvocationIngressAdapter,
        task_store: InMemoryTaskStore,
    ) -> None:
        await direct_adapter.invoke("查看现在有哪些严重 bug", user_id="bob")
        analyze_report = await direct_adapter.invoke("分析第1个bug", user_id="bob")
        bug_id = analyze_report.bugfix.evidence.bug_id if analyze_report.bugfix and analyze_report.bugfix.evidence else "BUG-001"
        report = await direct_adapter.invoke(f"生成修复工单 #{bug_id}", user_id="bob")
        assert report.intent == TaskIntent.GENERATE_FIX_ORDER
        assert report.bugfix is not None
        assert report.bugfix.work_order is not None
        assert report.bugfix.risk is not None

        events = task_store.list_events(report.task_id)
        event_types = [e.event_type for e in events]
        assert "task_created" in event_types
        assert "work_order_compiled" in event_types

    @pytest.mark.asyncio
    async def test_full_flow_events(
        self,
        direct_adapter: DirectInvocationIngressAdapter,
        task_store: InMemoryTaskStore,
    ) -> None:
        await direct_adapter.invoke("查看现在有哪些严重 bug", user_id="carol")
        analyze = await direct_adapter.invoke("分析第1个bug", user_id="carol")
        assert analyze.bugfix and analyze.bugfix.evidence
        bug_id = analyze.bugfix.evidence.bug_id
        analyze_events = task_store.list_events(analyze.task_id)
        assert "evidence_built" in [e.event_type for e in analyze_events]

        order = await direct_adapter.invoke(f"生成修复工单 #{bug_id}", user_id="carol")
        order_events = task_store.list_events(order.task_id)
        assert "work_order_compiled" in [e.event_type for e in order_events]
