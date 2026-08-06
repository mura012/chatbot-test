"""sample/ ディレクトリからテキストファイルを読み込む。"""

from __future__ import annotations

from pathlib import Path

from chatbot.rag.models import Document

TEXT_EXTENSIONS = {".txt", ".md"}


def load_documents(directory: Path) -> list[Document]:
    """指定ディレクトリ内の .txt / .md をすべて読み込む（README.md は除外）。"""
    if not directory.is_dir():
        raise FileNotFoundError(f"知識ベースのディレクトリが見つかりません: {directory}")

    documents: list[Document] = []
    for path in sorted(directory.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if path.name.upper() == "README.MD":
            continue

        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue

        documents.append(Document(source=path.name, content=content))

    if not documents:
        raise ValueError(f"読み込めるドキュメントがありません: {directory}")

    return documents
