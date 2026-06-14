from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    return datetime.now(UTC)


class NormalizedMessage(BaseModel):
    """跨入口统一消息模型；禁止携带 Hermes/HTTP 等平台原始字段。"""

    message_id: str
    user_id: str | None
    text: str
    source: Literal["direct"] = "direct"  # Phase 1 仅 direct；Hermes 接入后扩展 Literal
    created_at: datetime = Field(default_factory=_utc_now)
