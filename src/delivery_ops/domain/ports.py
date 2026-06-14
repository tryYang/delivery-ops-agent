"""领域端口：application 依赖这些 Protocol，由 adapters/storage/graphs 实现。"""

from __future__ import annotations

from typing import Protocol

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
