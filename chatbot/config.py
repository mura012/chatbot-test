"""環境変数から設定を読み込むモジュール。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """アプリケーション全体の設定値。"""

    openai_api_key: str | None
    openai_model: str
    embedding_model: str
    backend: str  # "openai" | "rule" | "openai_rag" | "rule_rag" | "rag"
    system_prompt: str
    host: str
    port: int
    knowledge_dir: Path
    rag_top_k: int
    rag_retriever: str  # "keyword" | "embedding"

    @classmethod
    def from_env(cls) -> Settings:
        api_key = os.getenv("OPENAI_API_KEY") or None
        backend = os.getenv("CHATBOT_BACKEND", "").lower()

        valid_backends = ("openai", "rule", "openai_rag", "rule_rag", "rag", "")
        if backend not in valid_backends:
            raise ValueError(
                f"CHATBOT_BACKEND は {', '.join(valid_backends[:-1])} のいずれかを指定してください"
                f"（現在: {backend}）"
            )

        if backend == "rag":
            backend = "openai_rag" if api_key else "rule_rag"
        elif backend == "":
            # デフォルトは RAG モード（API キーがあれば OpenAI RAG、なければルール RAG）
            backend = "openai_rag" if api_key else "rule_rag"

        rag_retriever = os.getenv("CHATBOT_RAG_RETRIEVER", "").lower()
        if rag_retriever not in ("keyword", "embedding", ""):
            raise ValueError(
                "CHATBOT_RAG_RETRIEVER は 'keyword' または 'embedding' を指定してください"
            )
        if rag_retriever == "":
            # embedding は API キーがある RAG モードでデフォルト
            rag_retriever = "embedding" if api_key and backend.endswith("_rag") else "keyword"

        knowledge_dir = Path(os.getenv("CHATBOT_KNOWLEDGE_DIR", "sample"))

        return cls(
            openai_api_key=api_key,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            backend=backend,
            system_prompt=os.getenv(
                "CHATBOT_SYSTEM_PROMPT",
                "あなたは親切で簡潔に答えるアシスタントです。日本語で応答してください。",
            ),
            host=os.getenv("CHATBOT_HOST", "127.0.0.1"),
            port=int(os.getenv("CHATBOT_PORT", "8000")),
            knowledge_dir=knowledge_dir,
            rag_top_k=int(os.getenv("CHATBOT_RAG_TOP_K", "3")),
            rag_retriever=rag_retriever,
        )

    @property
    def is_rag_backend(self) -> bool:
        return self.backend.endswith("_rag")


def get_settings() -> Settings:
    return Settings.from_env()
