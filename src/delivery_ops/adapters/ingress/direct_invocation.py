from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from delivery_ops.application.ingress_service import IngressService
from delivery_ops.domain.messages import NormalizedMessage
from delivery_ops.domain.reports import AgentReport


class DirectInvocationIngressAdapter:
    """Driving Adapter：将 (text, user_id) 转为领域消息，屏蔽调用方协议细节。"""

    def __init__(self, ingress_service: IngressService) -> None:
        self._ingress_service = ingress_service

    async def invoke(self, text: str, user_id: str | None = None) -> AgentReport:
        # source=direct 标识首期入口；Hermes 接入时仅改 adapter，不动 IngressService。
        message = NormalizedMessage(
            message_id=uuid4().hex,
            user_id=user_id,
            text=text,
            created_at=datetime.now(UTC),
        )
        return await self._ingress_service.handle_message(message)
