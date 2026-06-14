from __future__ import annotations

import pytest

from delivery_ops.adapters.requirements.fake_requirement_source import FakeRequirementSourceAdapter
from delivery_ops.application.evidence.feature_evidence_builder import FeatureEvidenceBuilder
from delivery_ops.application.feature.dependency_mapper import DependencyMapper
from delivery_ops.application.risk.feature_risk_planner import FeatureRiskPlanner
from delivery_ops.domain.features import FeatureRiskLevel


class TestFeatureRiskPlanner:
    @pytest.mark.asyncio
    async def test_payment_feature_high_risk(self) -> None:
        detail = await FakeRequirementSourceAdapter().get_feature_detail("FEAT-004")
        assert detail is not None
        deps = DependencyMapper().map(detail, None, None)
        packet = await FeatureEvidenceBuilder().build(detail, None, None, [], deps)
        risk = FeatureRiskPlanner().assess(detail, packet, deps)
        assert risk.level == FeatureRiskLevel.HIGH
        assert risk.auto_executable is False

    @pytest.mark.asyncio
    async def test_cms_feature_lower_risk(self) -> None:
        detail = await FakeRequirementSourceAdapter().get_feature_detail("FEAT-005")
        assert detail is not None
        deps = DependencyMapper().map(detail, None, None)
        packet = await FeatureEvidenceBuilder().build(detail, None, None, [], deps)
        risk = FeatureRiskPlanner().assess(detail, packet, deps)
        assert risk.level in {FeatureRiskLevel.LOW, FeatureRiskLevel.MEDIUM}
