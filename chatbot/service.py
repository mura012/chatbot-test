"""会話セッションの管理と応答生成を行うサービス層。"""

from __future__ import annotations

from chatbot.backends.base import ReplyBackend
from chatbot.backends.openai import OpenAIReplyBackend
from chatbot.backends.rule_based import RuleBasedReplyBackend
from chatbot.config import Settings, get_settings
from chatbot.models import Conversation, Message


class ChatService:
    """複数の会話セッションを管理し、バックエンドに応答生成を委譲する。"""

    def __init__(self, backend: ReplyBackend, settings: Settings) -> None:
        self._backend = backend
        self._settings = settings
        self._conversations: dict[str, Conversation] = {}

    @classmethod
    def create(cls, settings: Settings | None = None) -> ChatService:
        settings = settings or get_settings()
        backend = cls._build_backend(settings)
        return cls(backend=backend, settings=settings)

    @staticmethod
    def _build_backend(settings: Settings) -> ReplyBackend:
        if settings.backend == "openai":
            if not settings.openai_api_key:
                raise ValueError(
                    "CHATBOT_BACKEND=openai ですが OPENAI_API_KEY が設定されていません。"
                )
            return OpenAIReplyBackend(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
                system_prompt=settings.system_prompt,
            )
        return RuleBasedReplyBackend()

    @property
    def backend_name(self) -> str:
        return self._settings.backend

    def get_or_create_conversation(self, session_id: str | None = None) -> Conversation:
        if session_id and session_id in self._conversations:
            return self._conversations[session_id]

        conversation = Conversation()
        if session_id:
            conversation.id = session_id
        self._conversations[conversation.id] = conversation
        return conversation

    def chat(self, message: str, session_id: str | None = None) -> tuple[str, str, list[Message]]:
        """ユーザーメッセージを処理し、(応答テキスト, セッションID, 全会話メッセージ) を返す。"""
        conversation = self.get_or_create_conversation(session_id)

        reply = self._backend.generate_reply(conversation, message)

        conversation.add_user_message(message)
        conversation.add_assistant_message(reply)

        return reply, conversation.id, list(conversation.messages)

    def get_history(self, session_id: str) -> list[Message] | None:
        conversation = self._conversations.get(session_id)
        if conversation is None:
            return None
        return list(conversation.messages)

    def delete_conversation(self, session_id: str) -> bool:
        return self._conversations.pop(session_id, None) is not None
