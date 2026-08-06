"""チャンクの検索（リトリーバ）。"""

from __future__ import annotations

import math
import re
from abc import ABC, abstractmethod

from openai import OpenAI

from chatbot.rag.models import Chunk, RetrievedChunk


def _tokenize(text: str) -> set[str]:
    """日本語・英語混在テキストを検索用トークンに分解する（学習用の簡易実装）。"""
    tokens: set[str] = set()
    lowered = text.lower()
    tokens.update(re.findall(r"[a-z0-9]+", lowered))

    for segment in re.findall(r"[\u3040-\u30ff\u4e00-\u9fff]+", text):
        if len(segment) == 1:
            tokens.add(segment)
            continue
        tokens.add(segment)
        # 部分一致を拾うため、2〜4 文字のスライディングウィンドウも追加
        for size in (2, 3, 4):
            if len(segment) >= size:
                for i in range(len(segment) - size + 1):
                    tokens.add(segment[i : i + size])

    return tokens


def _score_tokens(query_tokens: set[str], content: str) -> float:
    """クエリトークンがコンテンツに含まれる割合をスコアとする。"""
    content_lower = content.lower()
    scorable = [t for t in query_tokens if len(t) >= 2 or t.isascii()]
    if not scorable:
        return 0.0

    hits = sum(1 for token in scorable if token in content or token in content_lower)
    return hits / len(scorable)


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: int) -> list[RetrievedChunk]:
        """クエリに関連するチャンクを上位 top_k 件返す。"""


class KeywordRetriever(BaseRetriever):
    """キーワードの重なりで関連チャンクを探す（DB・API 不要）。"""

    def __init__(self, chunks: list[Chunk]) -> None:
        self._chunks = chunks

    def retrieve(self, query: str, top_k: int) -> list[RetrievedChunk]:
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        scored: list[RetrievedChunk] = []
        for chunk in self._chunks:
            score = _score_tokens(query_tokens, chunk.content)
            if score > 0:
                scored.append(RetrievedChunk(chunk=chunk, score=score))

        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:top_k]


class EmbeddingRetriever(BaseRetriever):
    """OpenAI Embeddings API + メモリ上のベクトル類似度で検索する（DB 不要）。"""

    def __init__(
        self,
        chunks: list[Chunk],
        api_key: str,
        embedding_model: str = "text-embedding-3-small",
    ) -> None:
        self._chunks = chunks
        self._client = OpenAI(api_key=api_key)
        self._embedding_model = embedding_model
        self._vectors = self._embed_texts([c.content for c in chunks])

    def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = self._client.embeddings.create(
            model=self._embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    def retrieve(self, query: str, top_k: int) -> list[RetrievedChunk]:
        query_vector = self._embed_texts([query])[0]
        scored: list[RetrievedChunk] = []

        for chunk, vector in zip(self._chunks, self._vectors):
            score = _cosine_similarity(query_vector, vector)
            scored.append(RetrievedChunk(chunk=chunk, score=score))

        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:top_k]
