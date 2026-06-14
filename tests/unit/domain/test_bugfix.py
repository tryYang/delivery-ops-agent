from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from delivery_ops.domain.bugfix import (
    BugDetail,
    BugEvidencePacket,
    BugRiskAssessment,
    BugRiskLevel,
    BugSeverity,
    BugSummary,
    FixWorkOrder,
)


class TestBugfixModels:
    def test_bug_summary_valid(self) -> None:
        bug = BugSummary(
            bug_id="BUG-001",
            title="test",
            severity=BugSeverity.HIGH,
            status="open",
            module="auth",
            updated_at=datetime.now(UTC),
        )
        assert bug.bug_id == "BUG-001"

    def test_evidence_packet_sections(self) -> None:
        packet = BugEvidencePacket(
            bug_id="BUG-001",
            bug_facts=["fact"],
            prd_claims=[],
            code_facts=[],
            conflicts=[],
            unknowns=["missing prd"],
            suggested_scope=["src/auth/"],
        )
        assert packet.unknowns[0] == "missing prd"

    def test_invalid_severity_raises(self) -> None:
        with pytest.raises(ValidationError):
            BugDetail(
                bug_id="BUG-001",
                title="t",
                severity="invalid",  # type: ignore[arg-type]
                status="open",
                module="auth",
                description="d",
                reproduction="r",
            )

    def test_fix_work_order_fields(self) -> None:
        order = FixWorkOrder(
            objective="fix",
            evidence="e",
            allowed_scope=["src/a.py"],
            required_changes=["change"],
            acceptance_criteria=["pass"],
            forbidden=["refactor"],
            risk_level=BugRiskLevel.MEDIUM,
            verification_notes=["note"],
        )
        assert order.risk_level == BugRiskLevel.MEDIUM

    def test_risk_assessment(self) -> None:
        risk = BugRiskAssessment(
            level=BugRiskLevel.HIGH,
            reasons=["payment"],
            auto_executable=False,
        )
        assert risk.auto_executable is False
