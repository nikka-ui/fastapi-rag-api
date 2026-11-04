import os
from pathlib import Path


def chroma_path() -> str:
    """Vector store location. Defaults to %USERPROFILE%\\rag-api\\chroma_db."""
    override = os.getenv("CHROMA_PATH")
    if override:
        return str(Path(override).expanduser())
    return str(Path.home() / "rag-api" / "chroma_db")
