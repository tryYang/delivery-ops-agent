from __future__ import annotations

from datetime import UTC, datetime

from delivery_ops.application.bugfix.bug_severity_ranker import BugSeverityRanker
from delivery_ops.domain.bugfix import BugSeverity, BugSummary


class TestBugSeverityRanker:
    def setup_method(self) -> None:
        self.ranker = BugSeverityRanker()

    def test_rank_top_three_stable(self) -> None:
        bugs = [
            BugSummary(
                bug_id="BUG-LOW",
                title="minor typo",
                severity=BugSeverity.LOW,
                status="open",
                module="cms",
                updated_at=datetime.now(UTC),
            ),
            BugSummary(
                bug_id="BUG-CRIT",
                title="支付系统崩溃",
                severity=BugSeverity.CRITICAL,
                status="open",
                module="payment",
                updated_at=datetime.now(UTC),
            ),
            BugSummary(
                bug_id="BUG-MED",
                title="列表分页",
                severity=BugSeverity.MEDIUM,
                status="open",
                module="catalog",
                updated_at=datetime.now(UTC),
            ),
        ]
        scores = self.ranker.rank_top(bugs, limit=3)
        assert len(scores) == 3
        assert scores[0].bug_id == "BUG-CRIT"
        assert scores[0].score > scores[1].score
