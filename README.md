# chatbot-test

チャットボットの作り方を学ぶためのサンプルです。

**第3段階（この版）** では **RAG（検索拡張生成）** を導入しました。
`sample/` ディレクトリに置いた架空の作り話「霧晶の王国」だけを根拠に回答します。
データベースは使わず、メモリ上で検索します。

## 必要なもの

- Python 3.10 以上
- **ルールベース RAG**（`rule_rag`）: 追加の API キー不要
- **OpenAI RAG**（`openai_rag`）: [OpenAI API キー](https://platform.openai.com/api-keys) が必要（推奨）

## セットアップ

```bash
pip install -r requirements.txt
```

OpenAI で自然な文章の回答を得る場合:

```bash
export OPENAI_API_KEY=sk-...
export CHATBOT_BACKEND=openai_rag
```

## 動かし方

### Web UI（推奨）

```bash
python app.py
```

ブラウザで http://127.0.0.1:8000 を開きます。
回答と一緒に「参照した資料」が表示されます。

### CLI

```bash
python chatbot.py
```

### 試す質問の例

`sample/` の作り話にしか書いていない内容なので、RAG の動作確認に向いています。

- 「初代王アルドリックは誰？」
- 「霧晶魔法の三系統は？」
- 「アルセンは誰と出会った？」
- 「第五代国王は誰？」

## RAG の仕組み

```
ユーザーの質問
      │
      ▼
① sample/ から関連チャンクを検索（リトリーバ）
      │  ← DB ではなくメモリ上のインデックス
      ▼
② 検索結果を「参考資料」としてプロンプトに埋め込む
      │
      ▼
③ AI が参考資料だけを根拠に回答を生成
```

1. **読み込み** (`loader.py`) — `sample/*.txt` を読み込む
2. **チャンク分割** (`chunker.py`) — 段落単位で小さく分割
3. **検索** (`retriever.py`) — キーワード or Embeddings で関連チャンクを取得
4. **生成** (`rag_openai.py` / `rag_rule.py`) — チャンクをコンテキストに入れて回答

## バックエンドの種類

| `CHATBOT_BACKEND` | 説明 | API キー |
| --- | --- | --- |
| `rule_rag` | sample/ をキーワード検索し、結果を表示 | 不要 |
| `openai_rag` | sample/ を検索 + OpenAI で自然な回答 | 必要 |
| `rag` | キーの有無で上記を自動選択 | 任意 |
| `rule` | RAG なし・キーワードルールのみ | 不要 |
| `openai` | RAG なし・OpenAI のみ | 必要 |

省略時のデフォルト: API キーがあれば `openai_rag`、なければ `rule_rag`

## ファイル構成

| パス | 役割 |
| --- | --- |
| `sample/` | 架空世界「霧晶の王国」の作り話（知識ベース） |
| `chatbot/rag/` | RAG モジュール（読み込み・分割・検索） |
| `chatbot/backends/rag_openai.py` | OpenAI + RAG バックエンド |
| `chatbot/backends/rag_rule.py` | キーワード検索 + 整形表示 |
| `app.py` | FastAPI（Web API + UI） |
| `test_rag.py` | RAG 専用テスト |

## 環境変数

| 変数 | 説明 | デフォルト |
| --- | --- | --- |
| `OPENAI_API_KEY` | OpenAI API キー | 未設定 |
| `OPENAI_MODEL` | Chat 用モデル | `gpt-4o-mini` |
| `OPENAI_EMBEDDING_MODEL` | Embedding 用モデル | `text-embedding-3-small` |
| `CHATBOT_BACKEND` | バックエンド種別 | 上記参照 |
| `CHATBOT_KNOWLEDGE_DIR` | 知識ベースのディレクトリ | `sample` |
| `CHATBOT_RAG_TOP_K` | 取得するチャンク数 | `3` |
| `CHATBOT_RAG_RETRIEVER` | `keyword` または `embedding` | キーありなら `embedding` |

## テスト

```bash
python -m unittest discover -v
```

## API

`POST /api/chat` のレスポンスに `sources` フィールドが追加され、参照した資料が返ります。

```json
{
  "reply": "...",
  "session_id": "...",
  "backend": "rule_rag",
  "sources": [
    {
      "source": "王国の歴史.txt",
      "snippet": "初代王アルドリック・霧晶が王国を建国した...",
      "score": 0.75
    }
  ]
}
```

## 知識ベースを増やすには

`sample/` に `.txt` または `.md` ファイルを追加するだけです（DB 不要）。
アプリを再起動すると自動で読み込まれます。
