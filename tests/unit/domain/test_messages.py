from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from delivery_ops.domain.messages import NormalizedMessage


class TestNormalizedMessage:
    def test_required_fields(self) -> None:
        message = NormalizedMessage(
            message_id="msg-1",
            user_id="user-1",
            text="hello",
            created_at=datetime.now(UTC),
        )
        assert message.source == "direct"
        assert message.text == "hello"

    def test_missing_message_id_raises(self) -> None:
        with pytest.raises(ValidationError):
            NormalizedMessage(  # type: ignore[call-arg]
                user_id="user-1",
                text="hello",
            )
