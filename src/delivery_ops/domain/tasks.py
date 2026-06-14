from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field

from delivery_ops.domain.intents import TaskIntent, WorkflowType


def _utc_now() -> datetime:
    return datetime.now(UTC)


class TaskStatus(str, Enum):
    CREATED = "created"
    ANALYZING = "analyzing"
    WAITING_APPROVAL = "waiting_approval"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskSnapshot(BaseModel):
    """任务当前状态；状态变更须同步 append TaskEvent，不可只改快照。"""

    task_id: str
    workflow_type: WorkflowType
    intent: TaskIntent
    status: TaskStatus
    user_id: str | None
    input_text: str
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)


class TaskEvent(BaseModel):
    """追加式审计记录；event_type 如 task_created、task_status_changed。"""

    event_id: str
    task_id: str
    event_type: str
    payload: dict[str, str | int | float | bool | None]
    created_at: datetime = Field(default_factory=_utc_now)
