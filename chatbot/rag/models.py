"""RAG で使うデータ型。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    """sample/ から読み込んだ1ファイル分のテキスト。"""

    source: str  # ファイル名（例: 王国の歴史.txt）
    content: str


@dataclass(frozen=True)
class Chunk:
    """検索対象となるテキストの断片。"""

    source: str
    content: str
    index: int  # 同一ファイル内でのチャンク番号


@dataclass(frozen=True)
class RetrievedChunk:
    """検索でヒットしたチャンクとスコア。"""

    chunk: Chunk
    score: float
