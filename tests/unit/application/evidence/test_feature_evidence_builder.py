from __future__ import annotations

import pytest

from delivery_ops.adapters.design.fake_design_adapter import FakeDesignAdapter
from delivery_ops.adapters.prd.fake_feature_prd_reader import FakeFeaturePrdReader
from delivery_ops.adapters.repo.fake_feature_repo_search import FakeFeatureRepoSearch
from delivery_ops.adapters.requirements.fake_requirement_source import FakeRequirementSourceAdapter
from delivery_ops.application.design.design_context_service import DesignContextService
from delivery_ops.application.evidence.feature_evidence_builder import FeatureEvidenceBuilder
from delivery_ops.application.feature.dependency_mapper import DependencyMapper


class TestFeatureEvidenceBuilder:
    @pytest.mark.asyncio
    async def test_build_with_prd_and_design(self) -> None:
        detail = await FakeRequirementSourceAdapter().get_feature_detail("FEAT-001")
        assert detail is not None
        prd = await FakeFeaturePrdReader().read_and_analyze(detail)
        design = await DesignContextService(FakeDesignAdapter()).load(detail)
        hits = await FakeFeatureRepoSearch().search_reusable(detail)
        deps = DependencyMapper().map(detail, prd, design)
        packet = await FeatureEvidenceBuilder().build(detail, prd, design, hits, deps)
        assert packet.feature_id == "FEAT-001"
        assert packet.prd_claims
        assert packet.figma_claims
        assert packet.code_facts

    @pytest.mark.asyncio
    async def test_missing_prd_open_questions(self) -> None:
        detail = await FakeRequirementSourceAdapter().get_feature_detail("FEAT-003")
        assert detail is not None
        deps = DependencyMapper().map(detail, None, None)
        packet = await FeatureEvidenceBuilder().build(detail, None, None, [], deps)
        assert any("PRD" in q for q in packet.open_questions)
