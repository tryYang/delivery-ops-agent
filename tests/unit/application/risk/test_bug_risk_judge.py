from __future__ import annotations

import pytest

from delivery_ops.adapters.bug_sources.fake_bug_source import FakeBugSourceAdapter
from delivery_ops.application.evidence.bug_evidence_builder import BugEvidenceBuilder
from delivery_ops.application.risk.bug_risk_judge import BugRiskJudge
from delivery_ops.domain.bugfix import BugRiskLevel


class TestBugRiskJudge:
    @pytest.mark.asyncio
    async def test_payment_bug_is_high_risk(self) -> None:
        detail = await FakeBugSourceAdapter().get_bug_detail("BUG-001")
        assert detail is not None
        packet = await BugEvidenceBuilder().build(detail, None, [])
        risk = BugRiskJudge().assess(detail, packet)
        assert risk.level == BugRiskLevel.HIGH
        assert risk.auto_executable is False

    @pytest.mark.asyncio
    async def test_low_risk_cms_bug(self) -> None:
        detail = await FakeBugSourceAdapter().get_bug_detail("BUG-005")
        assert detail is not None
        packet = await BugEvidenceBuilder().build(detail, None, [])
        risk = BugRiskJudge().assess(detail, packet)
        assert risk.level in {BugRiskLevel.LOW, BugRiskLevel.MEDIUM}
