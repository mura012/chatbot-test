"""
コンソール（CLI）版チャットボット。

Web版（app.py）と同じ ChatService を使うので、
応答ロジック・会話履歴・RAG の扱いは Web と CLI で共通です。

使い方:
    python chatbot.py

環境変数でバックエンドを切り替え可能:
    CHATBOT_BACKEND=rule        → キーワードルール（RAG なし）
    CHATBOT_BACKEND=openai      → OpenAI API（RAG なし）
    CHATBOT_BACKEND=rule_rag    → sample/ を検索して固定表示（API 不要）
    CHATBOT_BACKEND=openai_rag  → sample/ を検索 + OpenAI で回答（推奨）
    CHATBOT_BACKEND=rag         → API キーの有無で openai_rag / rule_rag を自動選択
"""

from __future__ import annotations

from chatbot.config import get_settings
from chatbot.service import ChatService

EXIT_WORDS = {"exit", "quit", "終了", "bye", "さようなら"}


def is_exit_command(message: str) -> bool:
    return message.strip().lower() in EXIT_WORDS


def run_chat_loop() -> None:
    settings = get_settings()
    service = ChatService.create(settings)
    session_id: str | None = None

    backend_labels = {
        "openai": f"OpenAI ({settings.openai_model})",
        "rule": "ルールベース",
        "openai_rag": f"RAG + OpenAI ({settings.openai_model})",
        "rule_rag": f"RAG + キーワード検索",
    }
    backend_label = backend_labels.get(settings.backend, settings.backend)

    print("=== チャットボット（CLI） ===")
    print(f"バックエンド: {backend_label}")
    if settings.is_rag_backend:
        kb = service.knowledge_base
        if kb:
            print(f"知識ベース: {kb.directory}（{kb.document_count} ファイル / {kb.chunk_count} チャンク）")
    print(f"終了するには {', '.join(sorted(EXIT_WORDS))} のいずれかを入力してください。")
    print()

    while True:
        try:
            user_message = input("あなた: ")
        except (EOFError, KeyboardInterrupt):
            print("\nボット: またお話しましょう！")
            break

        if not user_message.strip():
            continue

        if is_exit_command(user_message):
            print("ボット: またお話しましょう！")
            break

        try:
            reply, session_id, _, sources = service.chat(user_message, session_id=session_id)
            print(f"ボット: {reply}")
            if sources:
                print("  [参照資料]")
                for src in sources:
                    preview = src.snippet[:80] + ("…" if len(src.snippet) > 80 else "")
                    print(f"    - {src.source} (score={src.score}): {preview}")
        except Exception as exc:
            print(f"ボット: エラーが発生しました — {exc}")


if __name__ == "__main__":
    run_chat_loop()
