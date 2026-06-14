from __future__ import annotations

from datetime import UTC, datetime

from delivery_ops.domain.bugfix import BugSeverity, BugSeverityScore, BugSummary

_SEVERITY_WEIGHT: dict[BugSeverity, float] = {
    BugSeverity.CRITICAL: 100.0,
    BugSeverity.HIGH: 80.0,
    BugSeverity.MEDIUM: 50.0,
    BugSeverity.LOW: 20.0,
}

_IMPACT_KEYWORDS: tuple[tuple[str, float], ...] = (
    ("支付", 15.0),
    ("订单", 12.0),
    ("登录", 10.0),
    ("生产", 20.0),
    ("critical", 10.0),
)


class BugSeverityRanker:
    def rank_top(self, bugs: list[BugSummary], limit: int = 3) -> list[BugSeverityScore]:
        scores = [self._score(bug) for bug in bugs]
        scores.sort(key=lambda item: item.score, reverse=True)
        return scores[:limit]

    def _score(self, bug: BugSummary) -> BugSeverityScore:
        reasons: list[str] = []
        total = _SEVERITY_WEIGHT[bug.severity]
        reasons.append(f"severity={bug.severity.value} (+{total})")

        title_lower = bug.title.lower()
        for keyword, bonus in _IMPACT_KEYWORDS:
            if keyword.lower() in title_lower:
                total += bonus
                reasons.append(f"impact keyword '{keyword}' (+{bonus})")

        age_days = (datetime.now(UTC) - bug.updated_at).days
        age_bonus = min(age_days * 0.5, 10.0)
        if age_bonus > 0:
            total += age_bonus
            reasons.append(f"open {age_days}d (+{age_bonus})")

        return BugSeverityScore(bug_id=bug.bug_id, score=total, reasons=reasons)
