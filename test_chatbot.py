"""chatbot パッケージの単体テスト。"""

import unittest
from unittest.mock import MagicMock, patch

from chatbot.backends.rule_based import RuleBasedReplyBackend
from chatbot.config import Settings
from chatbot.models import Conversation, Role
from chatbot.service import ChatService


def _base_settings(**kwargs) -> Settings:
    defaults = {
        "openai_api_key": None,
        "openai_model": "gpt-4o-mini",
        "embedding_model": "text-embedding-3-small",
        "backend": "rule",
        "system_prompt": "test",
        "host": "127.0.0.1",
        "port": 8000,
        "knowledge_dir": __import__("pathlib").Path("sample"),
        "rag_top_k": 3,
        "rag_retriever": "keyword",
    }
    defaults.update(kwargs)
    return Settings(**defaults)


class RuleBasedBackendTests(unittest.TestCase):
    def setUp(self) -> None:
        self.backend = RuleBasedReplyBackend()
        self.conversation = Conversation()

    def test_greeting(self) -> None:
        result = self.backend.generate_reply(self.conversation, "こんにちは")
        self.assertEqual(result.text, "こんにちは！今日はどんなご用件ですか？")

    def test_unknown_message(self) -> None:
        result = self.backend.generate_reply(self.conversation, "散歩に行きたい")
        self.assertIn("散歩に行きたい", result.text)


class ConversationTests(unittest.TestCase):
    def test_add_messages(self) -> None:
        conv = Conversation()
        conv.add_user_message("hello")
        conv.add_assistant_message("hi")
        self.assertEqual(len(conv.messages), 2)
        self.assertEqual(conv.messages[0].role, Role.USER)
        self.assertEqual(conv.messages[1].role, Role.ASSISTANT)

    def test_api_messages_with_system_prompt(self) -> None:
        conv = Conversation()
        conv.add_user_message("test")
        messages = conv.api_messages(system_prompt="You are helpful.")
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")


class ChatServiceTests(unittest.TestCase):
    def test_chat_creates_session_and_stores_history(self) -> None:
        service = ChatService.create(_base_settings(backend="rule"))

        reply1, session_id, messages1, _ = service.chat("こんにちは")
        self.assertIn("こんにちは", reply1)
        self.assertTrue(session_id)

        reply2, same_id, messages2, _ = service.chat("ありがとう", session_id=session_id)
        self.assertEqual(same_id, session_id)
        self.assertIn("どういたしまして", reply2)
        self.assertEqual(len(messages2), 4)

    def test_rule_rag_returns_sources(self) -> None:
        service = ChatService.create(_base_settings(backend="rule_rag"))
        reply, session_id, _, sources = service.chat("アルドリックは誰")
        self.assertTrue(session_id)
        self.assertGreater(len(sources), 0)
        self.assertIn("アルドリック", reply)

    def test_delete_conversation(self) -> None:
        service = ChatService.create(_base_settings(backend="rule"))
        _, session_id, _, _ = service.chat("hello")
        self.assertTrue(service.delete_conversation(session_id))
        self.assertIsNone(service.get_history(session_id))


class OpenAIBackendTests(unittest.TestCase):
    def test_openai_backend_calls_api(self) -> None:
        from chatbot.backends.openai import OpenAIReplyBackend

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "AIからの応答"
        mock_client.chat.completions.create.return_value = mock_response

        with patch("chatbot.backends.openai.OpenAI", return_value=mock_client):
            backend = OpenAIReplyBackend(
                api_key="test-key",
                model="gpt-4o-mini",
                system_prompt="Be helpful.",
            )
            conv = Conversation()
            result = backend.generate_reply(conv, "質問です")

        self.assertEqual(result.text, "AIからの応答")
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        self.assertEqual(call_kwargs["model"], "gpt-4o-mini")
        messages = call_kwargs["messages"]
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[-1]["content"], "質問です")


if __name__ == "__main__":
    unittest.main()
