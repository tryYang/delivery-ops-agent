from __future__ import annotations

from delivery_ops.domain.features import (
    FeatureEvidencePacket,
    FeatureRiskAssessment,
    FeatureSummary,
    RankedFeature,
)


def _session_key(user_id: str | None) -> str:
    return user_id or "__anonymous__"


class InMemoryFeatureSession:
    """按 user 保存 Feature Top 列表与 evidence；与 BugFixSession 物理隔离。"""

    def __init__(self) -> None:
        self._ranked_by_user: dict[str, list[RankedFeature]] = {}
        self._evidence_by_feature: dict[str, FeatureEvidencePacket] = {}
        self._risk_by_feature: dict[str, FeatureRiskAssessment] = {}

    def save_ranked_features(self, user_id: str | None, features: list[RankedFeature]) -> None:
        self._ranked_by_user[_session_key(user_id)] = list(features)

    def get_ranked_features(self, user_id: str | None) -> list[FeatureSummary] | None:
        ranked = self._ranked_by_user.get(_session_key(user_id))
        if ranked is None:
            return None
        return [FeatureSummary.model_validate(f.model_dump()) for f in ranked]

    def save_evidence(self, packet: FeatureEvidencePacket) -> None:
        self._evidence_by_feature[packet.feature_id] = packet

    def get_evidence(self, feature_id: str) -> FeatureEvidencePacket | None:
        return self._evidence_by_feature.get(feature_id)

    def save_risk(self, feature_id: str, risk: FeatureRiskAssessment) -> None:
        self._risk_by_feature[feature_id] = risk

    def get_risk(self, feature_id: str) -> FeatureRiskAssessment | None:
        return self._risk_by_feature.get(feature_id)
