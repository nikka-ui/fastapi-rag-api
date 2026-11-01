import httpx

from app.config import settings


async def generate(prompt: str) -> str:
    url = f"{settings.ollama_host.rstrip('/')}/api/generate"
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
    return data.get("response", "").strip()


async def healthcheck() -> dict:
    url = f"{settings.ollama_host.rstrip('/')}/api/tags"
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        models = [item.get("name") for item in response.json().get("models", [])]
    return {
        "ollama": "ok",
        "host": settings.ollama_host,
        "model": settings.ollama_model,
        "available_models": models,
        "model_present": settings.ollama_model in models
        or any(name.startswith(settings.ollama_model) for name in models),
    }
