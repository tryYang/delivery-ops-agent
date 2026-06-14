from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    return datetime.now(UTC)


class BugSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class BugRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class BugSummary(BaseModel):
    bug_id: str
    title: str
    severity: BugSeverity
    status: str
    module: str
    updated_at: datetime = Field(default_factory=_utc_now)


class BugDetail(BugSummary):
    description: str
    reproduction: str
    comments: list[str] = Field(default_factory=list)
    prd_hint: str | None = None


class BugSeverityScore(BaseModel):
    bug_id: str
    score: float
    reasons: list[str]


class RankedBug(BugSummary):
    score: float
    reasons: list[str]


class PrdRef(BaseModel):
    prd_id: str
    title: str
    url: str | None
    found_via: str


class PrdDocument(BaseModel):
    prd_id: str
    claims: list[str]


class CodeHit(BaseModel):
    path: str
    symbol: str
    line_hint: int | None
    reason: str


class BugEvidencePacket(BaseModel):
    bug_id: str
    bug_facts: list[str]
    prd_claims: list[str]
    code_facts: list[str]
    conflicts: list[str]
    unknowns: list[str]
    suggested_scope: list[str]


class BugRiskAssessment(BaseModel):
    level: BugRiskLevel
    reasons: list[str]
    auto_executable: bool


class FixWorkOrder(BaseModel):
    objective: str
    evidence: str
    allowed_scope: list[str]
    required_changes: list[str]
    acceptance_criteria: list[str]
    forbidden: list[str]
    risk_level: BugRiskLevel
    verification_notes: list[str]


class BugFixArtifacts(BaseModel):
    top_bugs: list[RankedBug] | None = None
    evidence: BugEvidencePacket | None = None
    work_order: FixWorkOrder | None = None
    risk: BugRiskAssessment | None = None
