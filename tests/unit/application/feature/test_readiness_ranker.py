from __future__ import annotations

from datetime import UTC, datetime

from delivery_ops.application.feature.feature_readiness_ranker import FeatureReadinessRanker
from delivery_ops.domain.features import FeatureDetail, FeaturePriority


class TestFeatureReadinessRanker:
    def setup_method(self) -> None:
        self.ranker = FeatureReadinessRanker()

    def test_rank_top_three(self) -> None:
        features = [
            FeatureDetail(
                feature_id="FEAT-LOW",
                title="minor",
                priority=FeaturePriority.P3,
                status="pending",
                target_release="2026-Q4",
                owner="pm",
                module="cms",
                updated_at=datetime.now(UTC),
                description="d",
            ),
            FeatureDetail(
                feature_id="FEAT-HIGH",
                title="payment",
                priority=FeaturePriority.P0,
                status="pending",
                target_release="2026-Q3",
                owner="pm",
                module="payment",
                updated_at=datetime.now(UTC),
                description="d",
                prd_id="PRD-1",
                figma_url="https://figma.example.com/x",
                dependencies_hint="gateway",
            ),
        ]
        scores = self.ranker.rank_top(features, limit=2)
        assert scores[0].feature_id == "FEAT-HIGH"
        assert scores[0].score > scores[1].score
