from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from delivery_ops.domain.tasks import TaskEvent, TaskSnapshot


class InMemoryTaskStore:
    """Phase 1 内存实现；生产环境替换为 DB 时保持 TaskStore Protocol 不变。"""

    def __init__(self) -> None:
        self._snapshots: dict[str, TaskSnapshot] = {}
        self._events: dict[str, list[TaskEvent]] = {}

    async def create_snapshot(self, snapshot: TaskSnapshot) -> None:
        self._snapshots[snapshot.task_id] = snapshot
        self._events.setdefault(snapshot.task_id, [])
        # 创建即审计：Case Library 依赖完整事件链，不能只存最终快照。
        await self.append_event(
            TaskEvent(
                event_id=uuid4().hex,
                task_id=snapshot.task_id,
                event_type="task_created",
                payload={
                    "workflow_type": snapshot.workflow_type.value,
                    "intent": snapshot.intent.value,
                    "status": snapshot.status.value,
                },
                created_at=datetime.now(UTC),
            )
        )

    async def get_snapshot(self, task_id: str) -> TaskSnapshot | None:
        return self._snapshots.get(task_id)

    async def update_snapshot(self, snapshot: TaskSnapshot) -> None:
        self._snapshots[snapshot.task_id] = snapshot

    async def append_event(self, event: TaskEvent) -> None:
        self._events.setdefault(event.task_id, []).append(event)

    def list_events(self, task_id: str) -> list[TaskEvent]:
        return list(self._events.get(task_id, []))
