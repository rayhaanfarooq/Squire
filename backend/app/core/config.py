"""
Configuration settings for the Squire backend
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings"""
    ENV: str = os.getenv("ENV", "development")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///backend/data/squire.db")
    SOLACE_HOST: str = os.getenv("SOLACE_HOST", "")
    SOLACE_USERNAME: str = os.getenv("SOLACE_USERNAME", "")
    SOLACE_PASSWORD: str = os.getenv("SOLACE_PASSWORD", "")


settings = Settings()

