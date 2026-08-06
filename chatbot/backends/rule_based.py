"""キーワードマッチングによるルールベースの応答バックエンド。"""

from __future__ import annotations

from chatbot.backends.base import ReplyBackend
from chatbot.models import Conversation

RULES: list[tuple[list[str], str]] = [
    (["こんにちは", "こんにちわ", "hello", "hi"], "こんにちは！今日はどんなご用件ですか？"),
    (["おはよう"], "おはようございます！"),
    (["こんばんは"], "こんばんは！"),
    (["ありがとう", "thanks", "thank you"], "どういたしまして！お役に立てて嬉しいです。"),
    (["名前", "誰"], "私はサンプルチャットボットです。よろしくお願いします。"),
    (["天気"], "すみません、天気情報を調べる機能はまだありません。"),
    (["元気"], "私は元気です！あなたはいかがですか？"),
]

DEFAULT_REPLY = "なるほど、「{message}」ですね。（ルールベースモードでは固定の返答のみです）"


class RuleBasedReplyBackend(ReplyBackend):
    """前回のサンプルと同じ、キーワードに応じた固定応答を返すバックエンド。"""

    def generate_reply(self, conversation: Conversation, user_message: str) -> str:
        normalized = user_message.lower()

        for keywords, reply in RULES:
            for keyword in keywords:
                if keyword.lower() in normalized:
                    return reply

        return DEFAULT_REPLY.format(message=user_message)
