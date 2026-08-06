"""RAG 用のコンテキスト整形とプロンプト。"""

from __future__ import annotations

from chatbot.rag.models import RetrievedChunk
from chatbot.reply import SourceReference

RAG_SYSTEM_PROMPT = """あなたは「霧晶の王国」に関する質問に答えるアシスタントです。

以下のルールを厳守してください:
1. 「参考資料」に書かれている内容だけを根拠にして回答する
2. 参考資料にないことは推測せず、「参考資料にはその情報はありません」と答える
3. 日本語で簡潔に答える
4. 可能ならどの資料に基づくか分かるように答える"""


def build_context_block(retrieved: list[RetrievedChunk]) -> str:
    if not retrieved:
        return "（関連する参考資料は見つかりませんでした）"

    parts: list[str] = []
    for i, item in enumerate(retrieved, start=1):
        parts.append(
            f"【資料{i}: {item.chunk.source}】\n{item.chunk.content}"
        )
    return "\n\n".join(parts)


def to_source_references(retrieved: list[RetrievedChunk]) -> list[SourceReference]:
    refs: list[SourceReference] = []
    for item in retrieved:
        snippet = item.chunk.content
        if len(snippet) > 200:
            snippet = snippet[:200] + "…"
        refs.append(
            SourceReference(
                source=item.chunk.source,
                snippet=snippet,
                score=round(item.score, 4),
            )
        )
    return refs


def format_rule_based_rag_reply(query: str, retrieved: list[RetrievedChunk]) -> str:
    """OpenAI を使わない RAG モード用の応答（検索結果をそのまま整形して返す）。"""
    if not retrieved:
        return (
            "参考資料（sample/ ディレクトリ）から関連する情報が見つかりませんでした。"
            "霧晶の王国に関する別の言い回しで質問してみてください。"
        )

    lines = ["参考資料から以下の内容が見つかりました:\n"]
    for i, item in enumerate(retrieved, start=1):
        lines.append(f"--- 資料{i}: {item.chunk.source} ---")
        lines.append(item.chunk.content)
        lines.append("")

    lines.append(
        "（ルールベース RAG モードのため、上記を検索結果として表示しています。"
        "自然な文章での回答には CHATBOT_BACKEND=openai_rag と OPENAI_API_KEY を設定してください。）"
    )
    return "\n".join(lines)
