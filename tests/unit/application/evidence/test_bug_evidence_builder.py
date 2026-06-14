from __future__ import annotations

from datetime import UTC, datetime

import pytest

from delivery_ops.adapters.bug_sources.fake_bug_source import FakeBugSourceAdapter
from delivery_ops.adapters.prd.fake_prd_resolver import FakePrdResolver
from delivery_ops.adapters.repo.fake_repo_search import FakeRepoSearch
from delivery_ops.application.evidence.bug_evidence_builder import BugEvidenceBuilder


class TestBugEvidenceBuilder:
    @pytest.mark.asyncio
    async def test_build_with_prd(self) -> None:
        bug_source = FakeBugSourceAdapter()
        detail = await bug_source.get_bug_detail("BUG-001")
        assert detail is not None
        _ref, prd = await FakePrdResolver().resolve(detail)
        hits = await FakeRepoSearch().search(detail)
        packet = await BugEvidenceBuilder().build(detail, prd, hits)
        assert packet.bug_id == "BUG-001"
        assert packet.bug_facts
        assert packet.prd_claims
        assert packet.code_facts
        assert packet.conflicts

    @pytest.mark.asyncio
    async def test_build_without_prd_has_unknowns(self) -> None:
        bug_source = FakeBugSourceAdapter()
        detail = await bug_source.get_bug_detail("BUG-003")
        assert detail is not None
        hits = await FakeRepoSearch().search(detail)
        packet = await BugEvidenceBuilder().build(detail, None, hits)
        assert any("PRD" in u for u in packet.unknowns)
