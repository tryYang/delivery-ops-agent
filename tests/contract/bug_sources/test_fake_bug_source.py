from __future__ import annotations

import pytest

from delivery_ops.adapters.bug_sources.fake_bug_source import FakeBugSourceAdapter
from delivery_ops.domain.bugfix import BugSeverity


class TestFakeBugSourceAdapter:
    @pytest.mark.asyncio
    async def test_list_open_bugs(self) -> None:
        adapter = FakeBugSourceAdapter()
        bugs = await adapter.list_open_bugs()
        assert len(bugs) >= 5
        assert all(b.status == "open" for b in bugs)

    @pytest.mark.asyncio
    async def test_get_bug_detail_known(self) -> None:
        adapter = FakeBugSourceAdapter()
        detail = await adapter.get_bug_detail("BUG-001")
        assert detail is not None
        assert detail.severity == BugSeverity.CRITICAL

    @pytest.mark.asyncio
    async def test_get_bug_detail_missing(self) -> None:
        adapter = FakeBugSourceAdapter()
        assert await adapter.get_bug_detail("BUG-999") is None
