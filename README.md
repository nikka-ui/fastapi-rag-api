# Local FastAPI RAG API

A small RAG API that runs on your laptop. GitHub holds the **code and docs**. Chroma and Ollama stay **local**.

## Where data is saved

The vector store is **not** in this GitHub repo. It is written on your PC:

```text
%USERPROFILE%\rag-api\chroma_db
```

On this machine that is `C:\Users\IT Nikka\rag-api\chroma_db`.

Override it with `CHROMA_PATH` in a local `.env` (copy from `.env.example`). Do not commit `.env`.

| Piece | Where it lives |
| --- | --- |
| FastAPI app, `profile.txt` | this repo |
| Chroma index (`chroma_db/`) | `%USERPROFILE%\rag-api\chroma_db` |
| Embeddings | Ollama `nomic-embed-text` |
| Answers | Ollama `qwen2.5:0.5b` |
| Model files | `~/.ollama` (not in git) |

## Prerequisites

```powershell
ollama pull qwen2.5:0.5b
ollama pull nomic-embed-text
```

## Setup

You can keep running from `C:\Users\IT Nikka\rag-api`. This GitHub copy lives at `C:\dev\fastapi-rag-api` and uses the **same** Chroma folder by default.

```powershell
cd C:\dev\fastapi-rag-api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Build (or refresh) the local index from `profile.txt`:

```powershell
python build_knowledge_base.py
```

## Run

```powershell
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | API status and Chroma path |
| `POST` | `/documents` | Add profile text to Chroma |
| `GET` | `/ask` | Retrieve context, then answer with Ollama |

```powershell
curl.exe "http://127.0.0.1:8000/health"
curl.exe "http://127.0.0.1:8000/ask?question=What%20is%20Nikka%20learning"
```

## What stays off GitHub

- `chroma_db/` (rebuild with `python build_knowledge_base.py`)
- `venv/` / `.venv/`
- `.env`
- `~/.ollama`
