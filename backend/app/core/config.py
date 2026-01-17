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
    
    # Hardcoded GitHub configuration for PR Agent
    GITHUB_REPO_OWNER: str = os.getenv("GITHUB_REPO_OWNER", "facebook")
    GITHUB_REPO_NAME: str = os.getenv("GITHUB_REPO_NAME", "react")
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")  # Optional for higher rate limits
    
    # Hardcoded Google Docs URLs for Meeting Agent
    GOOGLE_DOCS_URLS: str = os.getenv("GOOGLE_DOCS_URLS", "")  # Comma-separated URLs


settings = Settings()

