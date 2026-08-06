"""OpenAI API + RAG の応答バックエンド。"""

from __future__ import annotations

from openai import OpenAI

from chatbot.backends.base import ReplyBackend
from chatbot.models import Conversation
from chatbot.rag.knowledge_base import KnowledgeBase
from chatbot.rag.prompt import RAG_SYSTEM_PROMPT, build_context_block, to_source_references
from chatbot.reply import ReplyResult


class OpenAIRAGReplyBackend(ReplyBackend):
    """sample/ の資料を検索し、取得したコンテキストを OpenAI に渡して回答を生成する。"""

    def __init__(
        self,
        api_key: str,
        model: str,
        knowledge_base: KnowledgeBase,
        top_k: int,
        system_prompt: str = RAG_SYSTEM_PROMPT,
    ) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._knowledge_base = knowledge_base
        self._top_k = top_k
        self._system_prompt = system_prompt

    def generate_reply(self, conversation: Conversation, user_message: str) -> ReplyResult:
        retrieved = self._knowledge_base.retrieve(user_message, top_k=self._top_k)
        context = build_context_block(retrieved)

        user_content = (
            f"参考資料:\n{context}\n\n"
            f"質問: {user_message}"
        )

        messages = conversation.api_messages(system_prompt=self._system_prompt)
        messages.append({"role": "user", "content": user_content})

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
        )

        content = response.choices[0].message.content
        if content is None:
            raise RuntimeError("OpenAI API が空の応答を返しました。")

        return ReplyResult(text=content, sources=to_source_references(retrieved))
