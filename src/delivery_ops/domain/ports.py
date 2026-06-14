"""领域端口：application 依赖这些 Protocol，由 adapters/storage/graphs 实现。"""

from __future__ import annotations

from typing import Protocol

from delivery_ops.domain.bugfix import (
    BugDetail,
    BugEvidencePacket,
    BugRiskAssessment,
    BugSummary,
    CodeHit,
    FixWorkOrder,
    PrdDocument,
    PrdRef,
)
from delivery_ops.domain.features import (
    DependencyMap,
    DesignContext,
    DesignRef,
    FeatureDetail,
    FeatureEvidencePacket,
    FeaturePrdAnalysis,
    FeatureRiskAssessment,
    FeatureSummary,
    FeatureWorkOrder,
)
from delivery_ops.domain.intents import TaskIntent
from delivery_ops.domain.messages import NormalizedMessage
from delivery_ops.domain.reports import AgentReport
from delivery_ops.domain.tasks import TaskEvent, TaskSnapshot


class IngressPort(Protocol):
    async def handle_message(self, message: NormalizedMessage) -> AgentReport: ...


class DirectInvocationAdapter(Protocol):
    async def invoke(self, text: str, user_id: str | None = None) -> AgentReport: ...


class TaskStore(Protocol):
    async def create_snapshot(self, snapshot: TaskSnapshot) -> None: ...

    async def get_snapshot(self, task_id: str) -> TaskSnapshot | None: ...

    async def append_event(self, event: TaskEvent) -> None: ...


class WorkflowGraph(Protocol):
    async def run_placeholder(
        self,
        intent: TaskIntent,
        message: NormalizedMessage,
    ) -> TaskSnapshot: ...


class BugSourceAdapter(Protocol):
    async def list_open_bugs(self) -> list[BugSummary]: ...

    async def get_bug_detail(self, bug_id: str) -> BugDetail | None: ...


class PrdResolverPort(Protocol):
    async def resolve(self, bug: BugDetail) -> tuple[PrdRef | None, PrdDocument | None]: ...


class RepoSearchPort(Protocol):
    async def search(self, bug: BugDetail) -> list[CodeHit]: ...


class BugEvidenceBuilderPort(Protocol):
    async def build(
        self,
        bug: BugDetail,
        prd: PrdDocument | None,
        code_hits: list[CodeHit],
    ) -> BugEvidencePacket: ...


class FixWorkOrderCompilerPort(Protocol):
    async def compile(
        self,
        packet: BugEvidencePacket,
        risk: BugRiskAssessment,
    ) -> FixWorkOrder: ...


class RequirementSourceAdapter(Protocol):
    async def list_pending_features(self) -> list[FeatureSummary]: ...

    async def get_feature_detail(self, feature_id: str) -> FeatureDetail | None: ...


class DesignAdapter(Protocol):
    async def resolve_design(self, feature: FeatureDetail) -> DesignRef | None: ...

    async def read_design_context(self, design_ref: DesignRef) -> DesignContext: ...


class FeaturePrdReaderPort(Protocol):
    async def read_and_analyze(self, feature: FeatureDetail) -> FeaturePrdAnalysis | None: ...


class FeatureRepoSearchPort(Protocol):
    async def search_reusable(self, feature: FeatureDetail) -> list[CodeHit]: ...


class FeatureEvidenceBuilderPort(Protocol):
    async def build(
        self,
        feature: FeatureDetail,
        prd: FeaturePrdAnalysis | None,
        design: DesignContext | None,
        code_hits: list[CodeHit],
        dependencies: DependencyMap,
    ) -> FeatureEvidencePacket: ...


class FeatureWorkOrderCompilerPort(Protocol):
    async def compile(
        self,
        packet: FeatureEvidencePacket,
        risk: FeatureRiskAssessment,
    ) -> FeatureWorkOrder: ...
