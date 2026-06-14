from __future__ import annotations

from datetime import UTC, datetime

import pytest

from delivery_ops.application.bugfix.bug_ref_parser import BugRefParseError, BugRefParser
from delivery_ops.domain.bugfix import BugSeverity, BugSummary


class TestBugRefParser:
    def setup_method(self) -> None:
        self.parser = BugRefParser()
        self.ranked = [
            BugSummary(
                bug_id="BUG-001",
                title="a",
                severity=BugSeverity.HIGH,
                status="open",
                module="payment",
                updated_at=datetime.now(UTC),
            ),
            BugSummary(
                bug_id="BUG-002",
                title="b",
                severity=BugSeverity.MEDIUM,
                status="open",
                module="auth",
                updated_at=datetime.now(UTC),
            ),
        ]

    def test_parse_by_index(self) -> None:
        assert self.parser.parse("分析第1个bug", self.ranked) == "BUG-001"
        assert self.parser.parse("分析第2个 bug", self.ranked) == "BUG-002"

    def test_parse_by_hash_id(self) -> None:
        assert self.parser.parse("analyze bug #BUG-003", None) == "BUG-003"

    def test_index_without_session_raises(self) -> None:
        with pytest.raises(BugRefParseError):
            self.parser.parse("分析第1个bug", None)

    def test_index_out_of_range_raises(self) -> None:
        with pytest.raises(BugRefParseError):
            self.parser.parse("分析第9个bug", self.ranked)
