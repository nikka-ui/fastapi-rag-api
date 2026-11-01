from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app import rag
from app.config import settings
from app.ollama_client import generate, healthcheck

app = FastAPI(
    title="Local FastAPI RAG API",
    description=(
        "Runs on your laptop. Uses Ollama (qwen2.5:0.5b by default) for generation "
        "and BM25 over files in data/docs for retrieval. The model weights stay local."
    ),
    version="0.1.0",
)


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1)


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    k: int = Field(3, ge=1, le=8)


@app.get("/health")
async def health():
    try:
        ollama = await healthcheck()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Ollama is not reachable: {exc}") from exc
    return {"api": "ok", **ollama}


@app.post("/chat")
async def chat(body: ChatRequest):
    try:
        answer = await generate(body.prompt)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Ollama generate failed: {exc}") from exc
    return {"model": settings.ollama_model, "answer": answer}


@app.post("/ingest")
def ingest():
    return rag.build_index()


@app.post("/query")
async def query(body: QueryRequest):
    hits = rag.retrieve(body.question, k=body.k)
    prompt = rag.rag_prompt(body.question, hits)
    try:
        answer = await generate(prompt)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Ollama generate failed: {exc}") from exc
    return {
        "model": settings.ollama_model,
        "answer": answer,
        "sources": hits,
    }
