from __future__ import annotations

import pytest

from delivery_ops.adapters.requirements.fake_requirement_source import FakeRequirementSourceAdapter
from delivery_ops.domain.features import FeaturePriority


class TestFakeRequirementSourceAdapter:
    @pytest.mark.asyncio
    async def test_list_pending(self) -> None:
        adapter = FakeRequirementSourceAdapter()
        features = await adapter.list_pending_features()
        assert len(features) >= 5

    @pytest.mark.asyncio
    async def test_get_detail(self) -> None:
        adapter = FakeRequirementSourceAdapter()
        detail = await adapter.get_feature_detail("FEAT-001")
        assert detail is not None
        assert detail.priority == FeaturePriority.P0

    @pytest.mark.asyncio
    async def test_missing_detail(self) -> None:
        adapter = FakeRequirementSourceAdapter()
        assert await adapter.get_feature_detail("FEAT-999") is None
