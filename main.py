from fastapi import FastAPI
from pydantic import BaseModel
import ollama
import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

from paths import chroma_path

app = FastAPI(
    title="Local FastAPI RAG API",
    description="Runs on your laptop. Chroma saves under %USERPROFILE%\\rag-api\\chroma_db.",
)

client = chromadb.PersistentClient(path=chroma_path())

ef = OllamaEmbeddingFunction(
    model_name="nomic-embed-text",
    url="http://localhost:11434",
)

collection = client.get_or_create_collection(
    name="personal_profile",
    embedding_function=ef,
)


class DocumentSubmission(BaseModel):
    user_name: str
    content: str


@app.get("/health")
def health():
    return {
        "api": "ok",
        "chroma_path": chroma_path(),
        "collection": collection.name,
        "count": collection.count(),
    }


@app.post("/documents")
def add_document(submission: DocumentSubmission):
    chunks = [chunk.strip() for chunk in submission.content.split("\n\n") if chunk.strip()]

    collection.add(
        ids=[f"{submission.user_name}-chunk{i}" for i in range(len(chunks))],
        documents=chunks,
        metadatas=[
            {"source": "profile", "user_name": submission.user_name, "chunk_index": i}
            for i in range(len(chunks))
        ],
    )

    return {
        "message": f"Added {len(chunks)} chunks for user '{submission.user_name}'.",
        "user_name": submission.user_name,
        "chunks_added": len(chunks),
        "chroma_path": chroma_path(),
    }


@app.get("/ask")
def ask(question: str, user: str | None = None):
    query_params = {
        "query_texts": [question],
        "n_results": 2,
    }

    if user:
        query_params["where"] = {"user_name": user}

    results = collection.query(**query_params)
    documents = results["documents"][0] if results["documents"] else []
    context = "\n\n".join(documents)

    augmented_prompt = f"""Use the following context to answer the question.
If the context doesn't contain relevant information, say so.

Context:
{context}

Question: {question}"""

    response = ollama.chat(
        model="qwen2.5:0.5b",
        messages=[{"role": "user", "content": augmented_prompt}],
    )

    return {
        "question": question,
        "answer": response["message"]["content"],
        "context_used": documents,
        "filtered_by_user": user,
        "chroma_path": chroma_path(),
    }
