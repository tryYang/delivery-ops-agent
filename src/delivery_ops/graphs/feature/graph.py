from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from delivery_ops.domain.intents import TaskIntent, WorkflowType
from delivery_ops.domain.messages import NormalizedMessage
from delivery_ops.domain.tasks import TaskSnapshot, TaskStatus
from delivery_ops.storage.in_memory_task_store import InMemoryTaskStore


class FeatureGraph:
    """Feature Development 占位 Graph；与 BugFixGraph 物理隔离，禁止共享状态文件。"""

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
            workflow_type=WorkflowType.FEATURE_DEVELOPMENT,
            intent=intent,
            status=TaskStatus.ANALYZING,  # Phase 1 统一 analyzing，表示工作流已受理
            user_id=message.user_id,
            input_text=message.text,
            created_at=now,
            updated_at=now,
        )
        await self._task_store.create_snapshot(snapshot)
        return snapshot
