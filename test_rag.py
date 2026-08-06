"""RAG モジュールの単体テスト。"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from chatbot.backends.rag_rule import RuleBasedRAGReplyBackend
from chatbot.models import Conversation
from chatbot.rag.chunker import chunk_documents
from chatbot.rag.knowledge_base import KnowledgeBase
from chatbot.rag.loader import load_documents
from chatbot.rag.retriever import KeywordRetriever

SAMPLE_DIR = Path(__file__).parent / "sample"


class DocumentLoaderTests(unittest.TestCase):
    def test_load_sample_documents(self) -> None:
        docs = load_documents(SAMPLE_DIR)
        self.assertGreaterEqual(len(docs), 3)
        sources = {d.source for d in docs}
        self.assertIn("王国の歴史.txt", sources)
        self.assertIn("魔法の規則.txt", sources)
        self.assertIn("主人公の冒険.txt", sources)


class ChunkerTests(unittest.TestCase):
    def test_chunk_documents(self) -> None:
        docs = load_documents(SAMPLE_DIR)
        chunks = chunk_documents(docs)
        self.assertGreater(len(chunks), len(docs))


class KeywordRetrieverTests(unittest.TestCase):
    def setUp(self) -> None:
        docs = load_documents(SAMPLE_DIR)
        chunks = chunk_documents(docs)
        self.retriever = KeywordRetriever(chunks)

    def test_retrieve_kingdom_founding(self) -> None:
        results = self.retriever.retrieve("初代王アルドリックは誰", top_k=3)
        self.assertGreater(len(results), 0)
        combined = " ".join(r.chunk.content for r in results)
        self.assertIn("アルドリック", combined)

    def test_retrieve_adventure_character(self) -> None:
        results = self.retriever.retrieve("アルセンは誰と出会った", top_k=3)
        self.assertGreater(len(results), 0)
        combined = " ".join(r.chunk.content for r in results)
        self.assertIn("エリナ", combined)


class KnowledgeBaseTests(unittest.TestCase):
    def test_create_with_keyword_retriever(self) -> None:
        kb = KnowledgeBase.create(
            directory=SAMPLE_DIR,
            retriever_type="keyword",
            top_k=3,
        )
        self.assertEqual(kb.document_count, 3)
        self.assertGreater(kb.chunk_count, 0)

        results = kb.retrieve("霧晶魔法の三系統", top_k=2)
        self.assertGreater(len(results), 0)


class RuleBasedRAGBackendTests(unittest.TestCase):
    def test_generate_reply_with_sources(self) -> None:
        kb = KnowledgeBase.create(
            directory=SAMPLE_DIR,
            retriever_type="keyword",
            top_k=2,
        )
        backend = RuleBasedRAGReplyBackend(knowledge_base=kb, top_k=2)
        conv = Conversation()

        result = backend.generate_reply(conv, "第五代国王は誰")
        self.assertIn("レオン", result.text)
        self.assertGreater(len(result.sources), 0)


class OpenAIRAGBackendTests(unittest.TestCase):
    def test_openai_rag_includes_context(self) -> None:
        from chatbot.backends.rag_openai import OpenAIRAGReplyBackend

        kb = KnowledgeBase.create(
            directory=SAMPLE_DIR,
            retriever_type="keyword",
            top_k=2,
        )

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "レオン・霧晶です。"
        mock_client.chat.completions.create.return_value = mock_response

        with patch("chatbot.backends.rag_openai.OpenAI", return_value=mock_client):
            backend = OpenAIRAGReplyBackend(
                api_key="test-key",
                model="gpt-4o-mini",
                knowledge_base=kb,
                top_k=2,
            )
            conv = Conversation()
            result = backend.generate_reply(conv, "第五代国王は誰")

        self.assertEqual(result.text, "レオン・霧晶です。")
        self.assertGreater(len(result.sources), 0)

        messages = mock_client.chat.completions.create.call_args.kwargs["messages"]
        last_user = messages[-1]["content"]
        self.assertIn("参考資料", last_user)
        self.assertIn("第五代国王", last_user)


if __name__ == "__main__":
    unittest.main()
