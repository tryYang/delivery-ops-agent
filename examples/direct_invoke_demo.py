from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Allow running without editable install: python examples/direct_invoke_demo.py
_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

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
from delivery_ops.domain.reports import AgentReport
from delivery_ops.graphs.bugfix.graph import BugFixGraph
from delivery_ops.graphs.feature.graph import FeatureGraph
from delivery_ops.storage.in_memory_bug_fix_session import InMemoryBugFixSession
from delivery_ops.storage.in_memory_task_store import InMemoryTaskStore

DEMO_PROMPTS: tuple[tuple[str, str | None], ...] = (
    ("查看现在有哪些严重 bug", "alice"),
    ("分析第1个bug", "alice"),
    ("生成修复工单 #BUG-001", "alice"),
    ("查看当前迭代有哪些新功能", None),
    ("随便说句话", None),
)


def build_adapter() -> DirectInvocationIngressAdapter:
    task_store = InMemoryTaskStore()
    bugfix_session = InMemoryBugFixSession()
    ingress_service = IngressService(
        intent_router=IntentRouter(),
        workflow_router=WorkflowRouter(),
        bugfix_graph=BugFixGraph(
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
        ),
        feature_graph=FeatureGraph(task_store=task_store),
        system_handler=SystemHandler(task_store=task_store),
        report_publisher=ReportPublisher(),
    )
    return DirectInvocationIngressAdapter(ingress_service=ingress_service)


def format_report(report: AgentReport) -> str:
    return json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2)


async def invoke_once(
    adapter: DirectInvocationIngressAdapter,
    text: str,
    user_id: str | None,
) -> AgentReport:
    report = await adapter.invoke(text, user_id=user_id)
    print(f"\n>>> {text!r}")
    print(format_report(report))
    return report


async def run_demo(adapter: DirectInvocationIngressAdapter) -> None:
    for text, user_id in DEMO_PROMPTS:
        await invoke_once(adapter, text, user_id)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Direct invocation demo for Delivery Ops Agent (Phase 2 Bug Fix).",
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Custom message text. Omit to run built-in demo prompts.",
    )
    parser.add_argument("--user-id", default=None, help="Optional caller user id.")
    parser.add_argument(
        "--bugfix-flow",
        action="store_true",
        help="Run list → analyze #1 → work order in one process (same session).",
    )
    print(parser.parse_args())
    return parser.parse_args()


async def run_bugfix_flow(adapter: DirectInvocationIngressAdapter, user_id: str) -> None:
    list_report = await invoke_once(adapter, "查看现在有哪些严重 bug", user_id)
    if not list_report.bugfix or not list_report.bugfix.top_bugs:
        return
    bug_id = list_report.bugfix.top_bugs[0].bug_id
    await invoke_once(adapter, "分析第1个bug", user_id)
    await invoke_once(adapter, f"生成修复工单 #{bug_id}", user_id)


async def main() -> None:
    args = parse_args()
    adapter = build_adapter()

    if args.bugfix_flow:
        user_id = args.user_id or "demo-user"
        await run_bugfix_flow(adapter, user_id)
        return

    if args.text is not None:
        await invoke_once(adapter, args.text, args.user_id)
        if "第" in args.text and "个" in args.text:
            print(
                "\n提示：「第 N 个」依赖同进程内先执行 list。"
                "单次命令请用「分析 bug #BUG-001」，或加 --bugfix-flow。",
            )
        return

    print("Running built-in demo prompts (use --bugfix-flow for Bug Fix 三步链路):")
    await run_demo(adapter)


if __name__ == "__main__":
    asyncio.run(main())
