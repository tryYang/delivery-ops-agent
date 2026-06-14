from __future__ import annotations

from pydantic import BaseModel

from delivery_ops.domain.features import (
    FeatureArtifacts,
    FeatureEvidencePacket,
    FeatureWorkOrder,
    RankedFeature,
    FeatureRiskAssessment,
)
from delivery_ops.domain.intents import TaskIntent
from delivery_ops.domain.messages import NormalizedMessage
from delivery_ops.domain.tasks import TaskSnapshot


class FeatureState(BaseModel):
    intent: TaskIntent
    message: NormalizedMessage
    snapshot: TaskSnapshot | None = None
    ranked_features: list[RankedFeature] | None = None
    selected_feature_id: str | None = None
    evidence: FeatureEvidencePacket | None = None
    risk: FeatureRiskAssessment | None = None
    work_order: FeatureWorkOrder | None = None
    error: str | None = None

    def to_artifacts(self) -> FeatureArtifacts:
        return FeatureArtifacts(
            top_features=self.ranked_features,
            evidence=self.evidence,
            work_order=self.work_order,
            risk=self.risk,
        )
