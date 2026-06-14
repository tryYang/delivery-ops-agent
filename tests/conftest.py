from __future__ import annotations

import pytest

from delivery_ops.adapters.bug_sources.fake_bug_source import FakeBugSourceAdapter
from delivery_ops.adapters.ingress.direct_invocation import DirectInvocationIngressAdapter
from delivery_ops.adapters.prd.fake_prd_resolver import FakePrdResolver
from delivery_ops.adapters.repo.fake_repo_search import FakeRepoSearch
from delivery_ops.application.bugfix.bug_ref_parser import BugRefParser
from delivery_ops.application.bugfix.bug_severity_ranker import BugSeverityRanker
from delivery_ops.application.evidence.bug_evidence_builder import BugEvidenceBuilder
from delivery_ops.application.intent_router import IntentRouter
from delivery_ops.application.ingress_service import IngressService
from delivery_ops.application.report_publisher import ReportPublisher
from delivery_ops.application.risk.bug_risk_judge import BugRiskJudge
from delivery_ops.application.system_handler import SystemHandler
from delivery_ops.application.work_orders.fix_work_order_compiler import FixWorkOrderCompiler
from delivery_ops.application.workflow_router import WorkflowRouter
from delivery_ops.graphs.bugfix.graph import BugFixGraph
from delivery_ops.graphs.feature.graph import FeatureGraph
from delivery_ops.storage.in_memory_bug_fix_session import InMemoryBugFixSession
from delivery_ops.storage.in_memory_task_store import InMemoryTaskStore


@pytest.fixture
def task_store() -> InMemoryTaskStore:
    return InMemoryTaskStore()


@pytest.fixture
def bugfix_session() -> InMemoryBugFixSession:
    return InMemoryBugFixSession()


@pytest.fixture
def intent_router() -> IntentRouter:
    return IntentRouter()


@pytest.fixture
def workflow_router() -> WorkflowRouter:
    return WorkflowRouter()


@pytest.fixture
def report_publisher() -> ReportPublisher:
    return ReportPublisher()


@pytest.fixture
def bugfix_graph(task_store: InMemoryTaskStore, bugfix_session: InMemoryBugFixSession) -> BugFixGraph:
    return BugFixGraph(
        task_store=task_store,
        bug_source=FakeBugSourceAdapter(),
        prd_resolver=FakePrdResolver(),
        repo_search=FakeRepoSearch(),
        ranker=BugSeverityRanker(),
        ref_parser=BugRefParser(),
        evidence_builder=BugEvidenceBuilder(),
        risk_judge=BugRiskJudge(),
        work_order_compiler=FixWorkOrderCompiler(),
        session=bugfix_session,
    )


@pytest.fixture
def feature_graph(task_store: InMemoryTaskStore) -> FeatureGraph:
    return FeatureGraph(task_store=task_store)


@pytest.fixture
def system_handler(task_store: InMemoryTaskStore) -> SystemHandler:
    return SystemHandler(task_store=task_store)


@pytest.fixture
def ingress_service(
    intent_router: IntentRouter,
    workflow_router: WorkflowRouter,
    bugfix_graph: BugFixGraph,
    feature_graph: FeatureGraph,
    system_handler: SystemHandler,
    report_publisher: ReportPublisher,
) -> IngressService:
    return IngressService(
        intent_router=intent_router,
        workflow_router=workflow_router,
        bugfix_graph=bugfix_graph,
        feature_graph=feature_graph,
        system_handler=system_handler,
        report_publisher=report_publisher,
    )


@pytest.fixture
def direct_adapter(ingress_service: IngressService) -> DirectInvocationIngressAdapter:
    return DirectInvocationIngressAdapter(ingress_service=ingress_service)
