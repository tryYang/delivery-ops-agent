from __future__ import annotations

from datetime import UTC, datetime

from delivery_ops.domain.features import FeatureDetail, FeaturePriority, FeatureReadinessScore, FeatureSummary

_PRIORITY_WEIGHT: dict[FeaturePriority, float] = {
    FeaturePriority.P0: 100.0,
    FeaturePriority.P1: 75.0,
    FeaturePriority.P2: 50.0,
    FeaturePriority.P3: 25.0,
}


class FeatureReadinessRanker:
    def rank_top(self, features: list[FeatureSummary], limit: int = 3) -> list[FeatureReadinessScore]:
        scores = [self._score(f) for f in features]
        scores.sort(key=lambda item: item.score, reverse=True)
        return scores[:limit]

    def _score(self, feature: FeatureSummary) -> FeatureReadinessScore:
        reasons: list[str] = []
        total = _PRIORITY_WEIGHT[feature.priority]
        reasons.append(f"priority={feature.priority.value} (+{total})")

        if isinstance(feature, FeatureDetail):
            if feature.prd_id:
                total += 15.0
                reasons.append("prd linked (+15)")
            if feature.figma_url:
                total += 10.0
                reasons.append("figma linked (+10)")
            if feature.dependencies_hint:
                total += 5.0
                reasons.append("dependencies_hint present (+5)")

        if feature.target_release.startswith("2026-Q3"):
            total += 8.0
            reasons.append("near-term release (+8)")

        age_days = (datetime.now(UTC) - feature.updated_at).days
        if age_days <= 3:
            total += 5.0
            reasons.append(f"recently updated {age_days}d (+5)")

        return FeatureReadinessScore(feature_id=feature.feature_id, score=total, reasons=reasons)
