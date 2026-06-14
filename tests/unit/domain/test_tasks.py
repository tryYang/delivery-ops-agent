from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from delivery_ops.domain.intents import TaskIntent, WorkflowType
from delivery_ops.domain.tasks import TaskEvent, TaskSnapshot, TaskStatus


class TestTaskSnapshot:
    def test_valid_status_enum(self) -> None:
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
        assert snapshot.status == TaskStatus.ANALYZING

    def test_invalid_status_raises(self) -> None:
        with pytest.raises(ValidationError):
            TaskSnapshot(
                task_id="task-1",
                workflow_type=WorkflowType.BUG_FIX,
                intent=TaskIntent.ANALYZE_BUG,
                status="invalid",  # type: ignore[arg-type]
                user_id=None,
                input_text="analyze bug",
            )


class TestTaskEvent:
    def test_payload_type_constraint(self) -> None:
        event = TaskEvent(
            event_id="evt-1",
            task_id="task-1",
            event_type="task_created",
            payload={"status": "analyzing", "count": 1, "ok": True, "note": None},
            created_at=datetime.now(UTC),
        )
        assert event.payload["count"] == 1
