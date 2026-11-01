from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ollama_host: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen2.5:0.5b"
    docs_dir: str = "data/docs"
    index_path: str = "data/index.json"


settings = Settings()
