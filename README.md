# chatbot-test

チャットボットの作り方を学ぶためのサンプルです。

**第1段階（`main` の初期版）** では、固定文言だけの最小 CLI サンプルでした。
**この版** では、本格的な構成に拡張しています。

- **Web UI**（ブラウザで会話できるチャット画面）
- **REST API**（`POST /api/chat` など）
- **会話履歴（セッション）** の管理
- **バックエンドの切り替え**（ルールベース / OpenAI API）
- **モジュール分割**（設定・モデル・バックエンド・サービス層）

## 必要なもの

- Python 3.10 以上
- ルールベースモードだけ使う場合は追加の API キーは不要
- OpenAI モードを使う場合は [OpenAI API キー](https://platform.openai.com/api-keys)

## セットアップ

```bash
pip install -r requirements.txt
```

OpenAI を使う場合は環境変数を設定します（`.env.example` を参考）。

```bash
export OPENAI_API_KEY=sk-...
export CHATBOT_BACKEND=openai   # 省略時は API キーがあれば自動で openai
```

## 動かし方

### Web UI（推奨）

```bash
python app.py
```

ブラウザで http://127.0.0.1:8000 を開くとチャット画面が表示されます。

### CLI（コンソール）

```bash
python chatbot.py
```

Web と同じ `ChatService` を使うため、応答ロジック・会話履歴の扱いは共通です。

## テスト

```bash
python -m unittest discover -v
```

## アーキテクチャ

```
┌─────────────┐     ┌─────────────┐
│  Web UI     │     │  CLI        │
│  (static/)  │     │  chatbot.py │
└──────┬──────┘     └──────┬──────┘
       │                   │
       └─────────┬─────────┘
                 ▼
          ┌──────────────┐
          │   app.py     │  FastAPI（HTTP エンドポイント）
          └──────┬───────┘
                 ▼
          ┌──────────────┐
          │ ChatService  │  セッション管理・履歴保持
          └──────┬───────┘
                 ▼
       ┌─────────┴─────────┐
       ▼                   ▼
┌──────────────┐   ┌──────────────────┐
│ RuleBased    │   │ OpenAIReply      │
│ ReplyBackend │   │ Backend          │
│ (キーワード)  │   │ (Chat Completions)│
└──────────────┘   └──────────────────┘
```

### ファイル構成

| パス | 役割 |
| --- | --- |
| `app.py` | FastAPI アプリ（Web API + 静的ファイル配信） |
| `chatbot.py` | CLI 版エントリポイント |
| `chatbot/config.py` | 環境変数から設定を読み込む |
| `chatbot/models.py` | `Message`, `Conversation` などのデータ型 |
| `chatbot/service.py` | 会話セッションの管理と応答生成の窓口 |
| `chatbot/backends/rule_based.py` | キーワードルールによる応答（API 不要） |
| `chatbot/backends/openai.py` | OpenAI API による応答 |
| `static/` | Web チャット UI（HTML / CSS / JS） |
| `test_chatbot.py` | コアロジックのテスト |
| `test_app.py` | API エンドポイントのテスト |

## API エンドポイント

| メソッド | パス | 説明 |
| --- | --- | --- |
| `GET` | `/` | チャット UI |
| `GET` | `/api/health` | 稼働状況・使用中バックエンド |
| `POST` | `/api/chat` | メッセージを送って応答を得る |
| `GET` | `/api/history/{session_id}` | 会話履歴を取得 |
| `DELETE` | `/api/session/{session_id}` | セッションを削除 |

### `POST /api/chat` の例

```bash
curl -s -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "こんにちは"}'
```

```json
{
  "reply": "こんにちは！今日はどんなご用件ですか？",
  "session_id": "abc-123-...",
  "backend": "rule",
  "messages": [
    {"role": "user", "content": "こんにちは", "timestamp": "..."},
    {"role": "assistant", "content": "こんにちは！...", "timestamp": "..."}
  ]
}
```

同じ `session_id` を次のリクエストに含めると、会話の文脈が続きます。

## 環境変数

| 変数 | 説明 | デフォルト |
| --- | --- | --- |
| `OPENAI_API_KEY` | OpenAI API キー | 未設定 |
| `OPENAI_MODEL` | 使用モデル | `gpt-4o-mini` |
| `CHATBOT_BACKEND` | `openai` または `rule` | API キーがあれば `openai`、なければ `rule` |
| `CHATBOT_SYSTEM_PROMPT` | システムプロンプト（OpenAI 時） | 日本語アシスタント用の既定文 |
| `CHATBOT_HOST` | Web サーバーのホスト | `127.0.0.1` |
| `CHATBOT_PORT` | Web サーバーのポート | `8000` |

## 前回サンプルからの進化

| 項目 | 前回（最小版） | 今回（本格版） |
| --- | --- | --- |
| UI | CLI のみ | Web UI + CLI |
| 応答 | 固定ルールのみ | ルール / OpenAI を切り替え可能 |
| 会話履歴 | 保持しない | セッション ID で履歴を保持 |
| 構成 | 1 ファイル | パッケージ分割 + サービス層 |
| API | なし | REST API |
| テスト | 応答ロジックのみ | コア + API テスト |
