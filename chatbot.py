"""
コンソール（CLI）版チャットボット。

Web版（app.py）と同じ ChatService を使うので、
応答ロジック・会話履歴の扱いは Web と CLI で共通です。

使い方:
    python chatbot.py

環境変数でバックエンドを切り替え可能:
    CHATBOT_BACKEND=rule   → キーワードルール（APIキー不要）
    CHATBOT_BACKEND=openai → OpenAI API（OPENAI_API_KEY 必須）
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

    backend_label = (
        f"OpenAI ({settings.openai_model})"
        if settings.backend == "openai"
        else "ルールベース"
    )

    print("=== チャットボット（CLI） ===")
    print(f"バックエンド: {backend_label}")
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
            reply, session_id, _ = service.chat(user_message, session_id=session_id)
            print(f"ボット: {reply}")
        except Exception as exc:
            print(f"ボット: エラーが発生しました — {exc}")


if __name__ == "__main__":
    run_chat_loop()
