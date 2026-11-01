from __future__ import annotations

import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi

from app.config import settings

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def chunk_text(text: str, size: int = 400, overlap: int = 80) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    while start < len(words):
        end = min(len(words), start + size)
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(end - overlap, start + 1)
    return chunks


def load_documents(docs_dir: Path) -> list[dict]:
    records: list[dict] = []
    for path in sorted(docs_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".txt", ".md"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for i, chunk in enumerate(chunk_text(text)):
            records.append(
                {
                    "source": str(path.as_posix()),
                    "chunk_id": i,
                    "text": chunk,
                }
            )
    return records


def build_index() -> dict:
    docs_dir = Path(settings.docs_dir)
    docs_dir.mkdir(parents=True, exist_ok=True)
    records = load_documents(docs_dir)
    index_path = Path(settings.index_path)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"records": records}
    index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"chunks": len(records), "docs_dir": str(docs_dir)}


def _load_index() -> list[dict]:
    index_path = Path(settings.index_path)
    if not index_path.exists():
        build_index()
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    return payload.get("records", [])


def retrieve(query: str, k: int = 3) -> list[dict]:
    records = _load_index()
    if not records:
        return []
    corpus = [tokenize(item["text"]) for item in records]
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(tokenize(query))
    ranked = sorted(zip(scores, records), key=lambda pair: pair[0], reverse=True)
    hits = []
    for score, record in ranked[:k]:
        if score <= 0:
            continue
        hits.append({**record, "score": float(score)})
    return hits


def rag_prompt(question: str, hits: list[dict]) -> str:
    if not hits:
        context = "(no local documents matched)"
    else:
        context = "\n\n".join(
            f"[{i + 1}] source={hit['source']}\n{hit['text']}" for i, hit in enumerate(hits)
        )
    return (
        "You are a local RAG assistant. Answer the question using only the context. "
        "If the context is not enough, say you do not know.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    )
