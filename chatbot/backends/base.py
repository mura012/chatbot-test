"""応答バックエンドの抽象基底。"""

from __future__ import annotations

from abc import ABC, abstractmethod

from chatbot.models import Conversation
from chatbot.reply import ReplyResult


class ReplyBackend(ABC):
    """会話履歴を受け取り、次の応答を返すバックエンドの共通インターフェース。"""

    @abstractmethod
    def generate_reply(self, conversation: Conversation, user_message: str) -> ReplyResult:
        """ユーザーの最新メッセージと会話履歴から応答を生成する。"""
