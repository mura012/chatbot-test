"""環境変数から設定を読み込むモジュール。"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """アプリケーション全体の設定値。"""

    openai_api_key: str | None
    openai_model: str
    backend: str  # "openai" | "rule"
    system_prompt: str
    host: str
    port: int

    @classmethod
    def from_env(cls) -> Settings:
        api_key = os.getenv("OPENAI_API_KEY") or None
        backend = os.getenv("CHATBOT_BACKEND", "").lower()

        if backend not in ("openai", "rule", ""):
            raise ValueError(
                f"CHATBOT_BACKEND は 'openai' または 'rule' を指定してください（現在: {backend}）"
            )

        if backend == "":
            # APIキーがあれば OpenAI、なければルールベースを自動選択
            backend = "openai" if api_key else "rule"

        return cls(
            openai_api_key=api_key,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            backend=backend,
            system_prompt=os.getenv(
                "CHATBOT_SYSTEM_PROMPT",
                "あなたは親切で簡潔に答えるアシスタントです。日本語で応答してください。",
            ),
            host=os.getenv("CHATBOT_HOST", "127.0.0.1"),
            port=int(os.getenv("CHATBOT_PORT", "8000")),
        )


def get_settings() -> Settings:
    return Settings.from_env()
