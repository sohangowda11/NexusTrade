from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    FINNHUB_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    DATABASE_URL: str = "sqlite:///./trading.db"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    INITIAL_BALANCE: float = 100000.0
    MAX_AI_COST_PER_ANALYSIS: float = 0.50
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
