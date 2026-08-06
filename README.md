# chatbot-test

チャットボットの作り方を学ぶための、最低限のサンプルです。

- OpenAIなどの外部AIサービスには**一切リクエストを送りません**（ネットワーク通信なし）。
- 応答は「固定文言」または「キーワードに応じた簡単なルール分岐」のみで生成しています。
- AIライブラリ（例: `openai`, `langchain` など）は使わず、**Python標準ライブラリのみ**で動きます。追加インストールは不要です。

## 動かし方

Python 3.9 以上が入っていれば、追加のインストールなしですぐに動きます。

```bash
python3 chatbot.py
```

実行すると、コンソール上でチャットボットと対話できます。

```
=== サンプルチャットボット ===
終了するには bye, exit, quit, さようなら, 終了 のいずれかを入力してください。

あなた: こんにちは
ボット: こんにちは！今日はどんなご用件ですか？
あなた: ありがとう
ボット: どういたしまして！お役に立てて嬉しいです。
あなた: 終了
ボット: またお話しましょう！
```

会話を終了したいときは `exit` / `quit` / `終了` / `bye` / `さようなら` のいずれかを入力してください。
（`Ctrl+C` で強制終了することもできます）

## テストの実行

応答ロジック（`generate_reply` / `is_exit_command`）に対する簡単な単体テストも用意しています。

```bash
python -m unittest test_chatbot.py -v
```

## 中身の仕組み

チャットボットの最低限の仕組みは、実はとてもシンプルです。

1. ユーザーの入力を受け取る
2. 入力の内容を見て、返す言葉（応答）を決める
3. 応答を表示する
4. 1〜3を繰り返す（会話が終わるまでループする）

この「ループ」のことを、よく **会話ループ (conversation loop)** と呼びます。
本物のAIチャットボット（ChatGPTなど）も大枠の構造はこれと同じで、違うのは
「2. 応答を決める」部分が、固定ルールの代わりに**AIモデルへのAPIリクエスト**に
なっている、という点だけです。

このサンプルでは、その「2. 応答を決める」部分を `chatbot.py` の
`generate_reply()` という関数に切り出しています。

```python
def generate_reply(message: str) -> str:
    normalized = message.lower()
    for keywords, reply in RULES:
        for keyword in keywords:
            if keyword.lower() in normalized:
                return reply
    return DEFAULT_REPLY.format(message=message)
```

やっていることは非常に単純で、あらかじめ `RULES` に用意しておいた
「キーワード → 固定の返答」のペアを順番にチェックし、メッセージに
キーワードが含まれていればその返答を返す、というだけです。
どのルールにも一致しなければ、デフォルトの返答を返します。

### ファイル構成

| ファイル | 役割 |
| --- | --- |
| `chatbot.py` | チャットボット本体（会話ループ + 応答ロジック） |
| `test_chatbot.py` | 応答ロジックに対する単体テスト |

### 次のステップ（このサンプルでは実装していません）

将来的に本物のAI（例: OpenAI API）と連携させたくなったら、
会話ループなど他の部分はそのままに、`generate_reply()` の中身だけを
以下のようなイメージで差し替えれば実現できます。

```python
def generate_reply(message: str) -> str:
    response = openai_client.chat.completions.create(
        model="gpt-...",
        messages=[{"role": "user", "content": message}],
    )
    return response.choices[0].message.content
```

つまり「入力を受け取り、応答を決めて、表示する」という
チャットボットの骨組み自体は、ルールベースでもAIベースでも変わらない、
という点がこのサンプルで伝えたいポイントです。
