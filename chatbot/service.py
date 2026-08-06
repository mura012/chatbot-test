"""会話セッションの管理と応答生成を行うサービス層。"""

from __future__ import annotations

from chatbot.backends.base import ReplyBackend
from chatbot.backends.openai import OpenAIReplyBackend
from chatbot.backends.rag_openai import OpenAIRAGReplyBackend
from chatbot.backends.rag_rule import RuleBasedRAGReplyBackend
from chatbot.backends.rule_based import RuleBasedReplyBackend
from chatbot.config import Settings, get_settings
from chatbot.models import Conversation, Message
from chatbot.rag.knowledge_base import KnowledgeBase
from chatbot.reply import ReplyResult, SourceReference


class ChatService:
    """複数の会話セッションを管理し、バックエンドに応答生成を委譲する。"""

    def __init__(
        self,
        backend: ReplyBackend,
        settings: Settings,
        knowledge_base: KnowledgeBase | None = None,
    ) -> None:
        self._backend = backend
        self._settings = settings
        self._knowledge_base = knowledge_base
        self._conversations: dict[str, Conversation] = {}

    @classmethod
    def create(cls, settings: Settings | None = None) -> ChatService:
        settings = settings or get_settings()
        knowledge_base = cls._build_knowledge_base(settings) if settings.is_rag_backend else None
        backend = cls._build_backend(settings, knowledge_base)
        return cls(backend=backend, settings=settings, knowledge_base=knowledge_base)

    @staticmethod
    def _build_knowledge_base(settings: Settings) -> KnowledgeBase:
        return KnowledgeBase.create(
            directory=settings.knowledge_dir,
            retriever_type=settings.rag_retriever,
            top_k=settings.rag_top_k,
            openai_api_key=settings.openai_api_key,
            embedding_model=settings.embedding_model,
        )

    @staticmethod
    def _build_backend(
        settings: Settings,
        knowledge_base: KnowledgeBase | None,
    ) -> ReplyBackend:
        if settings.backend == "openai_rag":
            if not settings.openai_api_key:
                raise ValueError(
                    "CHATBOT_BACKEND=openai_rag ですが OPENAI_API_KEY が設定されていません。"
                )
            if knowledge_base is None:
                raise ValueError("RAG バックエンドには KnowledgeBase が必要です。")
            return OpenAIRAGReplyBackend(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
                knowledge_base=knowledge_base,
                top_k=settings.rag_top_k,
            )

        if settings.backend == "rule_rag":
            if knowledge_base is None:
                raise ValueError("RAG バックエンドには KnowledgeBase が必要です。")
            return RuleBasedRAGReplyBackend(
                knowledge_base=knowledge_base,
                top_k=settings.rag_top_k,
            )

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

    @property
    def knowledge_base(self) -> KnowledgeBase | None:
        return self._knowledge_base

    def get_or_create_conversation(self, session_id: str | None = None) -> Conversation:
        if session_id and session_id in self._conversations:
            return self._conversations[session_id]

        conversation = Conversation()
        if session_id:
            conversation.id = session_id
        self._conversations[conversation.id] = conversation
        return conversation

    def chat(
        self, message: str, session_id: str | None = None
    ) -> tuple[str, str, list[Message], list[SourceReference]]:
        """ユーザーメッセージを処理し、(応答, セッションID, 全会話, 参照ソース) を返す。"""
        conversation = self.get_or_create_conversation(session_id)

        result: ReplyResult = self._backend.generate_reply(conversation, message)

        conversation.add_user_message(message)
        conversation.add_assistant_message(result.text)

        return result.text, conversation.id, list(conversation.messages), result.sources

    def get_history(self, session_id: str) -> list[Message] | None:
        conversation = self._conversations.get(session_id)
        if conversation is None:
            return None
        return list(conversation.messages)

    def delete_conversation(self, session_id: str) -> bool:
        return self._conversations.pop(session_id, None) is not None
