from __future__ import annotations

from delivery_ops.domain.bugfix import BugEvidencePacket, BugRiskAssessment, BugSummary, RankedBug


def _session_key(user_id: str | None) -> str:
    return user_id or "__anonymous__"


class InMemoryBugFixSession:
    """按 user 保存 Top 列表、按 bug_id 保存 evidence，支持跨 invoke 的「第 N 个」解析。"""

    def __init__(self) -> None:
        self._ranked_by_user: dict[str, list[RankedBug]] = {}
        self._evidence_by_bug: dict[str, BugEvidencePacket] = {}
        self._risk_by_bug: dict[str, BugRiskAssessment] = {}

    def save_ranked_bugs(self, user_id: str | None, bugs: list[RankedBug]) -> None:
        self._ranked_by_user[_session_key(user_id)] = list(bugs)

    def get_ranked_bugs(self, user_id: str | None) -> list[BugSummary] | None:
        ranked = self._ranked_by_user.get(_session_key(user_id))
        if ranked is None:
            return None
        return [BugSummary.model_validate(b.model_dump()) for b in ranked]

    def save_evidence(self, packet: BugEvidencePacket) -> None:
        self._evidence_by_bug[packet.bug_id] = packet

    def get_evidence(self, bug_id: str) -> BugEvidencePacket | None:
        return self._evidence_by_bug.get(bug_id)

    def save_risk(self, bug_id: str, risk: BugRiskAssessment) -> None:
        self._risk_by_bug[bug_id] = risk

    def get_risk(self, bug_id: str) -> BugRiskAssessment | None:
        return self._risk_by_bug.get(bug_id)
