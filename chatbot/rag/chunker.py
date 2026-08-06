"""ドキュメントを検索しやすいサイズのチャンクに分割する。"""

from __future__ import annotations

import re

from chatbot.rag.models import Chunk, Document

# 段落（空行）で分割し、長すぎる段落はさらに分割する
MAX_CHUNK_CHARS = 600


def chunk_documents(documents: list[Document]) -> list[Chunk]:
    chunks: list[Chunk] = []

    for doc in documents:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", doc.content) if p.strip()]
        chunk_index = 0

        for paragraph in paragraphs:
            if len(paragraph) <= MAX_CHUNK_CHARS:
                chunks.append(Chunk(source=doc.source, content=paragraph, index=chunk_index))
                chunk_index += 1
                continue

            # 長い段落は文単位で分割して結合
            sentences = re.split(r"(?<=[。！？\n])", paragraph)
            buffer = ""
            for sentence in sentences:
                if len(buffer) + len(sentence) > MAX_CHUNK_CHARS and buffer:
                    chunks.append(Chunk(source=doc.source, content=buffer.strip(), index=chunk_index))
                    chunk_index += 1
                    buffer = sentence
                else:
                    buffer += sentence

            if buffer.strip():
                chunks.append(Chunk(source=doc.source, content=buffer.strip(), index=chunk_index))
                chunk_index += 1

    return chunks
