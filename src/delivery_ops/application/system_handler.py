from __future__ import annotations

import re
from datetime import UTC, datetime
from uuid import uuid4

from delivery_ops.domain.intents import TaskIntent, WorkflowType
from delivery_ops.domain.messages import NormalizedMessage
from delivery_ops.domain.tasks import TaskEvent, TaskSnapshot, TaskStatus
from delivery_ops.storage.in_memory_task_store import InMemoryTaskStore

# 从用户文本解析 #task_id；Hermes 接入后可改为结构化字段，避免正则依赖。
_TASK_ID_PATTERN = re.compile(r"#([\w-]+)")


class SystemHandler:
    """处理 task_status / cancel_task 等元操作，不生成 Evidence 或 Work Order。"""

    def __init__(self, task_store: InMemoryTaskStore) -> None:
        self._task_store = task_store

    async def handle(self, intent: TaskIntent, message: NormalizedMessage) -> TaskSnapshot:
        if intent == TaskIntent.TASK_STATUS:
            return await self._handle_task_status(message)
        if intent == TaskIntent.CANCEL_TASK:
            return await self._handle_cancel_task(message)
        msg = f"Unsupported system intent: {intent.value}"
        raise ValueError(msg)

    async def _handle_task_status(self, message: NormalizedMessage) -> TaskSnapshot:
        task_id = self._extract_task_id(message.text)
        if task_id is not None:
            existing = await self._task_store.get_snapshot(task_id)
            if existing is not None:
                return existing
        # 未找到 #task_id 时仍返回占位快照，保证调用方始终拿到结构化响应。
        return await self._create_system_snapshot(
            message=message,
            intent=TaskIntent.TASK_STATUS,
            status=TaskStatus.ANALYZING,
        )

    async def _handle_cancel_task(self, message: NormalizedMessage) -> TaskSnapshot:
        task_id = self._extract_task_id(message.text)
        if task_id is not None:
            existing = await self._task_store.get_snapshot(task_id)
            if existing is not None:
                now = datetime.now(UTC)
                cancelled = existing.model_copy(
                    update={"status": TaskStatus.CANCELLED, "updated_at": now}
                )
                await self._task_store.update_snapshot(cancelled)
                # 取消是状态变更，写入审计事件供 Case Library 追溯。
                await self._task_store.append_event(
                    TaskEvent(
                        event_id=uuid4().hex,
                        task_id=cancelled.task_id,
                        event_type="task_status_changed",
                        payload={"status": TaskStatus.CANCELLED.value},
                        created_at=now,
                    )
                )
                return cancelled
        # 目标 task 不存在时创建 cancelled 占位，与 task_status 行为对称。
        return await self._create_system_snapshot(
            message=message,
            intent=TaskIntent.CANCEL_TASK,
            status=TaskStatus.CANCELLED,
        )

    async def _create_system_snapshot(
        self,
        message: NormalizedMessage,
        intent: TaskIntent,
        status: TaskStatus,
    ) -> TaskSnapshot:
        now = datetime.now(UTC)
        snapshot = TaskSnapshot(
            task_id=uuid4().hex,
            workflow_type=WorkflowType.SYSTEM,
            intent=intent,
            status=status,
            user_id=message.user_id,
            input_text=message.text,
            created_at=now,
            updated_at=now,
        )
        await self._task_store.create_snapshot(snapshot)
        return snapshot

    @staticmethod
    def _extract_task_id(text: str) -> str | None:
        match = _TASK_ID_PATTERN.search(text)
        if match is None:
            return None
        return match.group(1)
