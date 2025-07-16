from dataclasses import dataclass, field
from datetime import datetime, UTC, timezone
from typing import Literal, List


@dataclass
class Message:
    role: Literal["user", "assistant", "system"]
    content: str


@dataclass
class ContextValue:
    messages: List[Message] = field(default_factory=list)
    last_interaction: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_message(self, role: Literal["user", "assistant", "system"], content: str) -> None:
        msg = Message(role=role, content=content)
        self.messages.append(msg)
        self.last_interaction = datetime.now(UTC)

    def get_history(self) -> list[dict]:
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in self.messages
        ]

    def trim(self, max_messages: int) -> None:
        if not isinstance(self.messages, list):
            return

        while len(self.messages) > max_messages:
             self.messages.pop(0)
