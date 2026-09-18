"""
Application configuration using pydantic-settings.
All sensitive values come from environment variables.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Sports AI Analytics"
    APP_VERSION: str = "2.1.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/sports_ai"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/sports_ai"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # AI / Qwen Configuration
    AI_PROVIDER: str = "qwen"
    QWEN_MODEL: str = "qwen-2.5-72b"
    QWEN_BASE_URL: str = "http://localhost:8080/v1"
    QWEN_API_KEY: str = ""
    QWEN_TIMEOUT: int = 120
    QWEN_MAX_TOKENS: int = 2000

    # Scraping
    SCRAPING_ENABLED: bool = True
    SCRAPING_INTERVAL_MINUTES: int = 60
    SCRAPING_TIMEOUT: int = 30
    SCRAPING_MAX_RETRIES: int = 3
    SCRAPING_USER_AGENT: str = "SportsAI-Analytics/2.1"

    # Prediction Models
    GOAL_MODEL_VERSION: str = "2.1.0"
    CORNER_MODEL_VERSION: str = "1.3.0"
    CARD_MODEL_VERSION: str = "1.1.0"
    PLAYER_MODEL_VERSION: str = "1.0.0"
    FEATURE_VERSION: str = "1.5.0"

    # Scheduler
    SCHEDULER_ENABLED: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
