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

from delivery_ops.adapters.ingress.direct_invocation import DirectInvocationIngressAdapter
from delivery_ops.application.intent_router import IntentRouter
from delivery_ops.application.ingress_service import IngressService
from delivery_ops.application.report_publisher import ReportPublisher
from delivery_ops.application.system_handler import SystemHandler
from delivery_ops.application.workflow_router import WorkflowRouter
from delivery_ops.domain.reports import AgentReport
from delivery_ops.graphs.bugfix.graph import BugFixGraph
from delivery_ops.graphs.feature.graph import FeatureGraph
from delivery_ops.storage.in_memory_task_store import InMemoryTaskStore

DEMO_PROMPTS: tuple[tuple[str, str | None], ...] = (
    ("查看现在有哪些严重 bug", "alice"),
    ("查看当前迭代有哪些新功能", None),
    ("查看任务 #demo-task-001", "alice"),
    ("随便说句话", None),
)


def build_adapter() -> DirectInvocationIngressAdapter:
    task_store = InMemoryTaskStore()
    ingress_service = IngressService(
        intent_router=IntentRouter(),
        workflow_router=WorkflowRouter(),
        bugfix_graph=BugFixGraph(task_store=task_store),
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
        description="Phase 1 direct invocation demo for Delivery Ops Agent.",
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Custom message text. Omit to run built-in demo prompts.",
    )
    parser.add_argument("--user-id", default=None, help="Optional caller user id.")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    adapter = build_adapter()

    if args.text is not None:
        await invoke_once(adapter, args.text, args.user_id)
        return

    print("Running built-in demo prompts (use positional text for a single invoke):")
    await run_demo(adapter)


if __name__ == "__main__":
    asyncio.run(main())
