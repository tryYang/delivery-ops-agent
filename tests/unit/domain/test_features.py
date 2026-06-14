from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from delivery_ops.domain.features import (
    FeatureEvidencePacket,
    FeaturePriority,
    FeatureRiskAssessment,
    FeatureRiskLevel,
    FeatureSummary,
    FeatureWorkOrder,
)


class TestFeatureModels:
    def test_feature_summary(self) -> None:
        f = FeatureSummary(
            feature_id="FEAT-001",
            title="t",
            priority=FeaturePriority.P0,
            status="pending",
            target_release="2026-Q3",
            owner="pm",
            module="order",
            updated_at=datetime.now(UTC),
        )
        assert f.feature_id == "FEAT-001"

    def test_evidence_packet(self) -> None:
        packet = FeatureEvidencePacket(
            feature_id="FEAT-001",
            requirement_facts=["fact"],
            prd_claims=[],
            figma_claims=[],
            code_facts=[],
            dependencies=[],
            conflicts=[],
            open_questions=["missing figma"],
            suggested_scope=["src/order/"],
        )
        assert packet.open_questions[0] == "missing figma"

    def test_invalid_priority(self) -> None:
        with pytest.raises(ValidationError):
            FeatureSummary(
                feature_id="FEAT-001",
                title="t",
                priority="x",  # type: ignore[arg-type]
                status="pending",
                target_release="2026-Q3",
                owner="pm",
                module="order",
            )

    def test_work_order(self) -> None:
        order = FeatureWorkOrder(
            objective="build",
            requirement_scope=["scope"],
            design_scope=["screen"],
            existing_code_to_reuse=["src/a.py"],
            required_changes=["change"],
            acceptance_criteria=["pass"],
            open_questions=[],
            forbidden=["refactor"],
            risk_level=FeatureRiskLevel.MEDIUM,
        )
        assert order.risk_level == FeatureRiskLevel.MEDIUM

    def test_risk_assessment(self) -> None:
        risk = FeatureRiskAssessment(
            level=FeatureRiskLevel.HIGH,
            reasons=["payment"],
            suggested_splits=["phase1"],
            auto_executable=False,
        )
        assert risk.auto_executable is False
