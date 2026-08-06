"""応答結果と参照ソース。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SourceReference:
    """RAG で参照したドキュメントの断片。"""

    source: str
    snippet: str
    score: float


@dataclass
class ReplyResult:
    text: str
    sources: list[SourceReference] = field(default_factory=list)
