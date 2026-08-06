"""FastAPI による Web チャットボットアプリケーション。"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from chatbot.config import get_settings
from chatbot.service import ChatService

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="Chatbot Sample",
    description="学習用チャットボット（ルールベース / OpenAI API / RAG）",
    version="3.0.0",
)

chat_service = ChatService.create()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="ユーザーのメッセージ")
    session_id: str | None = Field(None, description="既存の会話セッション ID（省略時は新規作成）")


class MessageResponse(BaseModel):
    role: str
    content: str
    timestamp: str


class SourceResponse(BaseModel):
    source: str
    snippet: str
    score: float


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    backend: str
    messages: list[MessageResponse]
    sources: list[SourceResponse] = []


class HealthResponse(BaseModel):
    status: str
    backend: str
    model: str | None = None
    rag_enabled: bool = False
    knowledge_dir: str | None = None
    knowledge_documents: int | None = None
    knowledge_chunks: int | None = None
    rag_retriever: str | None = None


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    kb = chat_service.knowledge_base

    return HealthResponse(
        status="ok",
        backend=chat_service.backend_name,
        model=settings.openai_model if settings.backend in ("openai", "openai_rag") else None,
        rag_enabled=settings.is_rag_backend,
        knowledge_dir=str(settings.knowledge_dir) if kb else None,
        knowledge_documents=kb.document_count if kb else None,
        knowledge_chunks=kb.chunk_count if kb else None,
        rag_retriever=settings.rag_retriever if kb else None,
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        reply, session_id, messages, sources = chat_service.chat(
            message=request.message.strip(),
            session_id=request.session_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"応答の生成に失敗しました: {exc}") from exc

    return ChatResponse(
        reply=reply,
        session_id=session_id,
        backend=chat_service.backend_name,
        messages=[
            MessageResponse(
                role=m.role.value,
                content=m.content,
                timestamp=m.timestamp.isoformat(),
            )
            for m in messages
        ],
        sources=[
            SourceResponse(source=s.source, snippet=s.snippet, score=s.score)
            for s in sources
        ],
    )


@app.get("/api/history/{session_id}", response_model=list[MessageResponse])
def get_history(session_id: str) -> list[MessageResponse]:
    messages = chat_service.get_history(session_id)
    if messages is None:
        raise HTTPException(status_code=404, detail="セッションが見つかりません。")
    return [
        MessageResponse(
            role=m.role.value,
            content=m.content,
            timestamp=m.timestamp.isoformat(),
        )
        for m in messages
    ]


@app.delete("/api/session/{session_id}")
def delete_session(session_id: str) -> dict[str, bool]:
    deleted = chat_service.delete_conversation(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="セッションが見つかりません。")
    return {"deleted": True}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run("app:app", host=settings.host, port=settings.port, reload=True)
