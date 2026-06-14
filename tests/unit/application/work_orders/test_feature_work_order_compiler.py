from __future__ import annotations

import pytest

from delivery_ops.adapters.requirements.fake_requirement_source import FakeRequirementSourceAdapter
from delivery_ops.application.evidence.feature_evidence_builder import FeatureEvidenceBuilder
from delivery_ops.application.feature.dependency_mapper import DependencyMapper
from delivery_ops.application.risk.feature_risk_planner import FeatureRiskPlanner
from delivery_ops.application.work_orders.feature_work_order_compiler import FeatureWorkOrderCompiler


class TestFeatureWorkOrderCompiler:
    @pytest.mark.asyncio
    async def test_compile_fields(self) -> None:
        detail = await FakeRequirementSourceAdapter().get_feature_detail("FEAT-001")
        assert detail is not None
        deps = DependencyMapper().map(detail, None, None)
        packet = await FeatureEvidenceBuilder().build(detail, None, None, [], deps)
        risk = FeatureRiskPlanner().assess(detail, packet, deps)
        order = await FeatureWorkOrderCompiler().compile(packet, risk)
        assert order.objective
        assert order.requirement_scope
        assert order.design_scope is not None
        assert order.existing_code_to_reuse is not None
        assert order.required_changes
        assert order.acceptance_criteria
        assert order.open_questions is not None
        assert order.forbidden
