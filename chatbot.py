"""
最低限のチャットボット サンプル
================================

このスクリプトは「チャットボットの作り方」を学ぶための、
できるだけシンプルにしたサンプルです。

ポイント:
- OpenAIなどの外部APIには一切アクセスしません（ネットワーク通信なし）。
- 返答は「固定文言」または「簡単なルール（キーワードに応じた分岐）」のみで生成します。
- Pythonの標準ライブラリだけで動くので、追加インストールは不要です。

チャットボットの最低限の仕組みは、実はとてもシンプルです。
    1. ユーザーの入力を受け取る
    2. 入力の内容を見て、返す言葉（応答）を決める
    3. 応答を表示する
    4. 1〜3を繰り返す（会話が終わるまでループする）

この「ループ」のことを、よく "会話ループ" (conversation loop) と呼びます。
本物のAIチャットボット（ChatGPTなど）も、大枠の構造はこれと同じで、
違うのは「2. 応答を決める」部分が、固定ルールの代わりに
AIモデルへのAPIリクエストになっている、という点だけです。

このサンプルでは、その「2. 応答を決める」部分を generate_reply() という
関数に切り出しています。将来的にOpenAI APIなどを使いたくなったときは、
この関数の中身だけを差し替えれば、会話ループなど他の部分はそのまま使えます。
"""

from __future__ import annotations


# 終了させたいときにユーザーが入力する言葉の一覧
EXIT_WORDS = {"exit", "quit", "終了", "bye", "さようなら"}

# キーワード → 固定応答 のルール一覧。
# 上から順番にチェックし、メッセージに含まれていれば、その返答を使う。
# （本来のAIチャットボットで言うと、ここが「学習済みモデル」に相当する部分）
RULES: list[tuple[list[str], str]] = [
    (["こんにちは", "こんにちわ", "hello", "hi"], "こんにちは！今日はどんなご用件ですか？"),
    (["おはよう"], "おはようございます！"),
    (["こんばんは"], "こんばんは！"),
    (["ありがとう", "thanks", "thank you"], "どういたしまして！お役に立てて嬉しいです。"),
    (["名前", "誰"], "私はサンプルチャットボットです。よろしくお願いします。"),
    (["天気"], "すみません、天気情報を調べる機能はまだありません（このサンプルには実装していません）。"),
    (["元気"], "私は元気です！あなたはいかがですか？"),
]

# どのルールにも一致しなかったときに返す、デフォルトの応答
DEFAULT_REPLY = "なるほど、「{message}」ですね。（このサンプルでは固定の返答しかできません）"


def generate_reply(message: str) -> str:
    """ユーザーからのメッセージを受け取り、返答の文字列を返す。

    ここでは実際のAI（大規模言語モデル）は一切使わず、
    「メッセージの中に特定のキーワードが含まれているか」だけをチェックして
    あらかじめ用意した固定文言を返している。

    本物のAPIと連携したくなったら、例えば以下のようなイメージで
    この関数の中身だけを書き換えれば良い（このサンプルでは実装しない）。

        def generate_reply(message: str) -> str:
            response = openai_client.chat.completions.create(...)
            return response.choices[0].message.content
    """
    normalized = message.lower()

    for keywords, reply in RULES:
        for keyword in keywords:
            if keyword.lower() in normalized:
                return reply

    return DEFAULT_REPLY.format(message=message)


def is_exit_command(message: str) -> bool:
    """ユーザーが会話を終了したいかどうかを判定する。"""
    return message.strip().lower() in EXIT_WORDS


def run_chat_loop() -> None:
    """コンソール上でユーザーと対話するメインループ。"""
    print("=== サンプルチャットボット ===")
    print(f"終了するには {', '.join(sorted(EXIT_WORDS))} のいずれかを入力してください。")
    print()

    while True:
        try:
            user_message = input("あなた: ")
        except (EOFError, KeyboardInterrupt):
            print("\nボット: またお話しましょう！")
            break

        if not user_message.strip():
            # 空メッセージのときは何も返さず、再度入力を待つ
            continue

        if is_exit_command(user_message):
            print("ボット: またお話しましょう！")
            break

        reply = generate_reply(user_message)
        print(f"ボット: {reply}")


if __name__ == "__main__":
    run_chat_loop()
