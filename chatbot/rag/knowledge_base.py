"""知識ベースの構築と検索の窓口（DB を使わずメモリ上で完結）。"""

from __future__ import annotations

from pathlib import Path

from chatbot.rag.chunker import chunk_documents
from chatbot.rag.loader import load_documents
from chatbot.rag.models import RetrievedChunk
from chatbot.rag.retriever import BaseRetriever, EmbeddingRetriever, KeywordRetriever


class KnowledgeBase:
    """sample/ などのディレクトリからドキュメントを読み込み、検索可能にする。"""

    def __init__(
        self,
        directory: Path,
        retriever: BaseRetriever,
        document_count: int,
        chunk_count: int,
    ) -> None:
        self._directory = directory
        self._retriever = retriever
        self._document_count = document_count
        self._chunk_count = chunk_count

    @classmethod
    def create(
        cls,
        directory: Path,
        retriever_type: str,
        top_k: int,  # noqa: ARG003 — create 時は未使用だが設定の一貫性のため受け取る
        openai_api_key: str | None = None,
        embedding_model: str = "text-embedding-3-small",
    ) -> KnowledgeBase:
        documents = load_documents(directory)
        chunks = chunk_documents(documents)

        if retriever_type == "embedding":
            if not openai_api_key:
                raise ValueError(
                    "CHATBOT_RAG_RETRIEVER=embedding ですが OPENAI_API_KEY が設定されていません。"
                )
            retriever: BaseRetriever = EmbeddingRetriever(
                chunks=chunks,
                api_key=openai_api_key,
                embedding_model=embedding_model,
            )
        else:
            retriever = KeywordRetriever(chunks=chunks)

        return cls(
            directory=directory,
            retriever=retriever,
            document_count=len(documents),
            chunk_count=len(chunks),
        )

    @property
    def directory(self) -> Path:
        return self._directory

    @property
    def document_count(self) -> int:
        return self._document_count

    @property
    def chunk_count(self) -> int:
        return self._chunk_count

    def retrieve(self, query: str, top_k: int) -> list[RetrievedChunk]:
        return self._retriever.retrieve(query, top_k=top_k)
