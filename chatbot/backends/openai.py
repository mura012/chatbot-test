"""OpenAI API を使った応答バックエンド。"""

from __future__ import annotations

from openai import OpenAI

from chatbot.backends.base import ReplyBackend
from chatbot.models import Conversation


class OpenAIReplyBackend(ReplyBackend):
    """OpenAI の Chat Completions API で応答を生成するバックエンド。"""

    def __init__(self, api_key: str, model: str, system_prompt: str) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._system_prompt = system_prompt

    def generate_reply(self, conversation: Conversation, user_message: str) -> str:
        # conversation には user_message がまだ追加されていない想定。
        # api_messages は system + 既存履歴のみを含め、最新ユーザー入力は別途渡す。
        messages = conversation.api_messages(system_prompt=self._system_prompt)
        messages.append({"role": "user", "content": user_message})

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
        )

        content = response.choices[0].message.content
        if content is None:
            raise RuntimeError("OpenAI API が空の応答を返しました。")
        return content
