from __future__ import annotations

from datetime import UTC, datetime

import pytest

from delivery_ops.domain.intents import TaskIntent, WorkflowType
from delivery_ops.domain.tasks import TaskEvent, TaskSnapshot, TaskStatus
from delivery_ops.storage.in_memory_task_store import InMemoryTaskStore


@pytest.fixture
def store() -> InMemoryTaskStore:
    return InMemoryTaskStore()


class TestInMemoryTaskStore:
    @pytest.mark.asyncio
    async def test_create_and_get_snapshot(self, store: InMemoryTaskStore) -> None:
        snapshot = TaskSnapshot(
            task_id="task-1",
            workflow_type=WorkflowType.BUG_FIX,
            intent=TaskIntent.ANALYZE_BUG,
            status=TaskStatus.ANALYZING,
            user_id=None,
            input_text="analyze bug",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        await store.create_snapshot(snapshot)
        loaded = await store.get_snapshot("task-1")
        assert loaded == snapshot

    @pytest.mark.asyncio
    async def test_events_appended_in_order(self, store: InMemoryTaskStore) -> None:
        snapshot = TaskSnapshot(
            task_id="task-2",
            workflow_type=WorkflowType.SYSTEM,
            intent=TaskIntent.TASK_STATUS,
            status=TaskStatus.CREATED,
            user_id=None,
            input_text="status",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        await store.create_snapshot(snapshot)
        await store.append_event(
            TaskEvent(
                event_id="evt-2",
                task_id="task-2",
                event_type="task_status_changed",
                payload={"status": "analyzing"},
                created_at=datetime.now(UTC),
            )
        )
        events = store.list_events("task-2")
        assert len(events) == 2
        assert events[0].event_type == "task_created"
        assert events[1].event_type == "task_status_changed"

    @pytest.mark.asyncio
    async def test_missing_task_returns_none(self, store: InMemoryTaskStore) -> None:
        assert await store.get_snapshot("missing") is None
