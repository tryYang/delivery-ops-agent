from __future__ import annotations

from pydantic import BaseModel

from delivery_ops.domain.bugfix import BugFixArtifacts
from delivery_ops.domain.intents import TaskIntent, WorkflowType
from delivery_ops.domain.tasks import TaskStatus


class AgentReport(BaseModel):
    task_id: str
    workflow_type: WorkflowType
    intent: TaskIntent
    status: TaskStatus
    message: str
    details: dict[str, str | int | float | bool | None]
    bugfix: BugFixArtifacts | None = None
