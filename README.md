# Local FastAPI RAG API

A small RAG API that runs on your laptop. GitHub holds the **code and docs**. Ollama holds the **model**.

This repo does **not** upload `C:\Users\<you>\.ollama`, model weights, or chat history.

## What this is

| Piece | Where it lives |
| --- | --- |
| FastAPI app | this repo |
| Retrieval | BM25 over `.txt` / `.md` files in `data/docs` |
| Generation | local Ollama model `qwen2.5:0.5b` |
| Model files | `~/.ollama` on your machine (not in git) |

Interactive chat in PowerShell is still:

```powershell
ollama run qwen2.5:0.5b
```

The API talks to the same model over `http://127.0.0.1:11434`.

## Prerequisites

1. Python 3.11+
2. [Ollama](https://ollama.com) installed and running
3. Pull the model (already done if you have been chatting locally):

```powershell
ollama pull qwen2.5:0.5b
```

Confirm Ollama is up:

```powershell
curl.exe http://127.0.0.1:11434/api/tags
```

## Setup

```powershell
cd C:\dev\fastapi-rag-api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

## Run

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open docs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | API + Ollama status |
| `POST` | `/chat` | Send a prompt to `qwen2.5:0.5b` |
| `POST` | `/ingest` | Rebuild the local BM25 index from `data/docs` |
| `POST` | `/query` | Retrieve passages, then answer with Ollama |

### Chat

```powershell
curl.exe -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d "{\"prompt\":\"Hello\"}"
```

### Ingest local documents

Put `.txt` or `.md` files in `data/docs`, then:

```powershell
curl.exe -X POST http://127.0.0.1:8000/ingest
```

### Ask with RAG

```powershell
curl.exe -X POST http://127.0.0.1:8000/query -H "Content-Type: application/json" -d "{\"question\":\"What is this project?\"}"
```

`qwen2.5:0.5b` is a small model. It is fast on a laptop and good for learning RAG wiring; answers will be weaker than larger models.

## What stays off GitHub

- `.env`
- `.venv/`
- `data/index.json` (rebuilt by `/ingest`)
- Your own documents in `data/docs` (a sample file is committed)
- `~/.ollama` (blobs, history, `id_ed25519` private key)

Anyone who clones this repo still needs Ollama on **their** machine:

```powershell
ollama pull qwen2.5:0.5b
```
