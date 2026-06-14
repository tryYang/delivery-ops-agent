from __future__ import annotations

from pydantic import BaseModel

from delivery_ops.domain.bugfix import (
    BugEvidencePacket,
    BugFixArtifacts,
    BugSummary,
    FixWorkOrder,
    RankedBug,
    BugRiskAssessment,
)
from delivery_ops.domain.intents import TaskIntent
from delivery_ops.domain.messages import NormalizedMessage
from delivery_ops.domain.tasks import TaskSnapshot


class BugFixState(BaseModel):
    intent: TaskIntent
    message: NormalizedMessage
    snapshot: TaskSnapshot | None = None
    ranked_bugs: list[RankedBug] | None = None
    selected_bug_id: str | None = None
    evidence: BugEvidencePacket | None = None
    risk: BugRiskAssessment | None = None
    work_order: FixWorkOrder | None = None
    error: str | None = None

    def to_artifacts(self) -> BugFixArtifacts:
        return BugFixArtifacts(
            top_bugs=self.ranked_bugs,
            evidence=self.evidence,
            work_order=self.work_order,
            risk=self.risk,
        )
