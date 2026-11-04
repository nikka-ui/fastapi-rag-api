import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

from paths import chroma_path

with open("profile.txt", "r", encoding="utf-8") as f:
    text = f.read()

chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]

print(f"Loaded {len(chunks)} chunks from profile.txt")
print(f"Saving Chroma DB to: {chroma_path()}")

client = chromadb.PersistentClient(path=chroma_path())

ef = OllamaEmbeddingFunction(
    model_name="nomic-embed-text",
    url="http://localhost:11434",
)

collection = client.get_or_create_collection(
    name="personal_profile",
    embedding_function=ef,
)

collection.add(
    ids=[f"chunk{i}" for i in range(len(chunks))],
    documents=chunks,
    metadatas=[{"source": "profile", "chunk_index": i} for i in range(len(chunks))],
)

print(f"Added {len(chunks)} chunks to the 'personal_profile' collection.")
print("Knowledge base built successfully!")
