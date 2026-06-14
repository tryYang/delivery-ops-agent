from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    return datetime.now(UTC)


class FeaturePriority(str, Enum):
    P0 = "p0"
    P1 = "p1"
    P2 = "p2"
    P3 = "p3"


class FeatureRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FeatureSummary(BaseModel):
    feature_id: str
    title: str
    priority: FeaturePriority
    status: str
    target_release: str
    owner: str
    module: str
    updated_at: datetime = Field(default_factory=_utc_now)


class FeatureDetail(FeatureSummary):
    description: str
    acceptance_hint: str | None = None
    prd_id: str | None = None
    figma_url: str | None = None
    dependencies_hint: str | None = None


class FeatureReadinessScore(BaseModel):
    feature_id: str
    score: float
    reasons: list[str]


class RankedFeature(FeatureSummary):
    score: float
    reasons: list[str]


class DesignRef(BaseModel):
    file_key: str
    node_id: str
    title: str
    url: str | None


class DesignContext(BaseModel):
    screens: list[str]
    components: list[str]
    states: list[str]
    annotations: list[str]


class DependencyItem(BaseModel):
    kind: str
    name: str
    description: str
    blocking: bool


class DependencyMap(BaseModel):
    items: list[DependencyItem]


class FeaturePrdAnalysis(BaseModel):
    prd_id: str
    scope: list[str]
    acceptance_criteria: list[str]
    boundaries: list[str]
    claims: list[str]


class FeatureEvidencePacket(BaseModel):
    feature_id: str
    requirement_facts: list[str]
    prd_claims: list[str]
    figma_claims: list[str]
    code_facts: list[str]
    dependencies: list[str]
    conflicts: list[str]
    open_questions: list[str]
    suggested_scope: list[str]


class FeatureRiskAssessment(BaseModel):
    level: FeatureRiskLevel
    reasons: list[str]
    suggested_splits: list[str]
    auto_executable: bool


class FeatureWorkOrder(BaseModel):
    objective: str
    requirement_scope: list[str]
    design_scope: list[str]
    existing_code_to_reuse: list[str]
    required_changes: list[str]
    acceptance_criteria: list[str]
    open_questions: list[str]
    forbidden: list[str]
    risk_level: FeatureRiskLevel


class FeatureArtifacts(BaseModel):
    top_features: list[RankedFeature] | None = None
    evidence: FeatureEvidencePacket | None = None
    work_order: FeatureWorkOrder | None = None
    risk: FeatureRiskAssessment | None = None
