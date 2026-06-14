from __future__ import annotations

from datetime import UTC, datetime

import pytest

from delivery_ops.application.feature.feature_ref_parser import FeatureRefParseError, FeatureRefParser
from delivery_ops.domain.features import FeaturePriority, FeatureSummary


class TestFeatureRefParser:
    def setup_method(self) -> None:
        self.parser = FeatureRefParser()
        self.ranked = [
            FeatureSummary(
                feature_id="FEAT-001",
                title="a",
                priority=FeaturePriority.P0,
                status="pending",
                target_release="2026-Q3",
                owner="pm",
                module="order",
                updated_at=datetime.now(UTC),
            ),
        ]

    def test_parse_by_index(self) -> None:
        assert self.parser.parse("分析第1个新功能", self.ranked) == "FEAT-001"

    def test_parse_by_hash_id(self) -> None:
        assert self.parser.parse("analyze feature #FEAT-003", None) == "FEAT-003"

    def test_index_without_session_raises(self) -> None:
        with pytest.raises(FeatureRefParseError):
            self.parser.parse("分析第1个新功能", None)
