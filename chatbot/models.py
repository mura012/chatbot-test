"""チャットボットで使うデータ型の定義。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    role: Role
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_api_dict(self) -> dict[str, str]:
        """OpenAI API などに渡す形式へ変換する。"""
        return {"role": self.role.value, "content": self.content}


@dataclass
class Conversation:
    """1つの会話セッション（メッセージ履歴を保持）。"""

    id: str = field(default_factory=lambda: str(uuid4()))
    messages: list[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_user_message(self, content: str) -> Message:
        message = Message(role=Role.USER, content=content)
        self.messages.append(message)
        return message

    def add_assistant_message(self, content: str) -> Message:
        message = Message(role=Role.ASSISTANT, content=content)
        self.messages.append(message)
        return message

    def api_messages(self, system_prompt: str | None = None) -> list[dict[str, str]]:
        """API に渡すメッセージ一覧（system + 履歴）。"""
        result: list[dict[str, str]] = []
        if system_prompt:
            result.append({"role": Role.SYSTEM.value, "content": system_prompt})
        result.extend(msg.to_api_dict() for msg in self.messages)
        return result
