"""応答生成バックエンド（ルールベース / OpenAI など）。"""

from chatbot.backends.base import ReplyBackend
from chatbot.backends.openai import OpenAIReplyBackend
from chatbot.backends.rule_based import RuleBasedReplyBackend

__all__ = ["ReplyBackend", "RuleBasedReplyBackend", "OpenAIReplyBackend"]
