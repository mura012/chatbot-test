"""ルールベース + RAG（キーワード検索）の応答バックエンド。"""

from __future__ import annotations

from chatbot.backends.base import ReplyBackend
from chatbot.models import Conversation
from chatbot.rag.knowledge_base import KnowledgeBase
from chatbot.rag.prompt import format_rule_based_rag_reply, to_source_references
from chatbot.reply import ReplyResult


class RuleBasedRAGReplyBackend(ReplyBackend):
    """sample/ の資料をキーワード検索し、ヒットした内容を整形して返す（OpenAI 不要）。"""

    def __init__(self, knowledge_base: KnowledgeBase, top_k: int) -> None:
        self._knowledge_base = knowledge_base
        self._top_k = top_k

    def generate_reply(self, conversation: Conversation, user_message: str) -> ReplyResult:
        retrieved = self._knowledge_base.retrieve(user_message, top_k=self._top_k)
        text = format_rule_based_rag_reply(user_message, retrieved)
        return ReplyResult(text=text, sources=to_source_references(retrieved))
