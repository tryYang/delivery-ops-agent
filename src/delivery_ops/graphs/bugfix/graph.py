from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from delivery_ops.domain.intents import TaskIntent, WorkflowType
from delivery_ops.domain.messages import NormalizedMessage
from delivery_ops.domain.tasks import TaskSnapshot, TaskStatus
from delivery_ops.storage.in_memory_task_store import InMemoryTaskStore


class BugFixGraph:
    """Bug Fix 占位 Graph；Phase 2 替换为 LangGraph，状态模型不与 Feature 共享。"""

    def __init__(self, task_store: InMemoryTaskStore) -> None:
        self._task_store = task_store

    async def run_placeholder(
        self,
        intent: TaskIntent,
        message: NormalizedMessage,
    ) -> TaskSnapshot:
        now = datetime.now(UTC)
        snapshot = TaskSnapshot(
            task_id=uuid4().hex,
            workflow_type=WorkflowType.BUG_FIX,
            intent=intent,
            status=TaskStatus.ANALYZING,  # Phase 1 统一 analyzing，表示工作流已受理
            user_id=message.user_id,
            input_text=message.text,
            created_at=now,
            updated_at=now,
        )
        await self._task_store.create_snapshot(snapshot)
        return snapshot
