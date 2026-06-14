from __future__ import annotations

import pytest

from delivery_ops.adapters.bug_sources.fake_bug_source import FakeBugSourceAdapter
from delivery_ops.application.evidence.bug_evidence_builder import BugEvidenceBuilder
from delivery_ops.application.risk.bug_risk_judge import BugRiskJudge
from delivery_ops.application.work_orders.fix_work_order_compiler import FixWorkOrderCompiler
from delivery_ops.domain.bugfix import BugRiskLevel


class TestFixWorkOrderCompiler:
    @pytest.mark.asyncio
    async def test_compile_eight_sections(self) -> None:
        detail = await FakeBugSourceAdapter().get_bug_detail("BUG-001")
        assert detail is not None
        packet = await BugEvidenceBuilder().build(detail, None, [])
        risk = BugRiskJudge().assess(detail, packet)
        order = await FixWorkOrderCompiler().compile(packet, risk)
        assert order.objective
        assert order.evidence
        assert order.allowed_scope
        assert order.required_changes
        assert order.acceptance_criteria
        assert order.forbidden
        assert order.risk_level == BugRiskLevel.HIGH
        assert order.verification_notes
        assert "自动执行" in " ".join(order.forbidden)
