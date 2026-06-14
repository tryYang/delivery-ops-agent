from __future__ import annotations

import pytest

from delivery_ops.adapters.ingress.direct_invocation import DirectInvocationIngressAdapter
from delivery_ops.domain.intents import TaskIntent
from delivery_ops.domain.tasks import TaskStatus
from delivery_ops.storage.in_memory_task_store import InMemoryTaskStore


class TestFeatureReadonlyFlow:
    @pytest.mark.asyncio
    async def test_list_features(self, direct_adapter: DirectInvocationIngressAdapter) -> None:
        report = await direct_adapter.invoke("查看当前迭代有哪些新功能", user_id="alice")
        assert report.intent == TaskIntent.LIST_FEATURE_TASKS
        assert report.feature is not None
        assert report.feature.top_features is not None
        assert len(report.feature.top_features) <= 3
        scores = [f.score for f in report.feature.top_features]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_analyze_first_feature(self, direct_adapter: DirectInvocationIngressAdapter) -> None:
        await direct_adapter.invoke("查看当前迭代有哪些新功能", user_id="alice")
        report = await direct_adapter.invoke("分析第1个新功能", user_id="alice")
        assert report.intent == TaskIntent.ANALYZE_FEATURE
        assert report.feature is not None
        assert report.feature.evidence is not None
        assert report.feature.risk is not None
        assert report.status == TaskStatus.WAITING_APPROVAL

    @pytest.mark.asyncio
    async def test_generate_feature_order(
        self,
        direct_adapter: DirectInvocationIngressAdapter,
        task_store: InMemoryTaskStore,
    ) -> None:
        await direct_adapter.invoke("查看当前迭代有哪些新功能", user_id="bob")
        analyze = await direct_adapter.invoke("分析第1个新功能", user_id="bob")
        fid = analyze.feature.evidence.feature_id if analyze.feature and analyze.feature.evidence else "FEAT-001"
        report = await direct_adapter.invoke(f"生成功能工单 #{fid}", user_id="bob")
        assert report.intent == TaskIntent.GENERATE_FEATURE_ORDER
        assert report.feature is not None
        assert report.feature.work_order is not None
        events = task_store.list_events(report.task_id)
        assert "work_order_compiled" in [e.event_type for e in events]

    @pytest.mark.asyncio
    async def test_full_flow_events(
        self,
        direct_adapter: DirectInvocationIngressAdapter,
        task_store: InMemoryTaskStore,
    ) -> None:
        await direct_adapter.invoke("查看当前迭代有哪些新功能", user_id="carol")
        analyze = await direct_adapter.invoke("分析第1个新功能", user_id="carol")
        assert analyze.feature and analyze.feature.evidence
        assert "evidence_built" in [e.event_type for e in task_store.list_events(analyze.task_id)]
        fid = analyze.feature.evidence.feature_id
        order = await direct_adapter.invoke(f"生成功能工单 #{fid}", user_id="carol")
        assert "work_order_compiled" in [e.event_type for e in task_store.list_events(order.task_id)]
