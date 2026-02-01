"""Strategem Core - Configuration Module"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""

    # API Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4000"))

    # Retry configuration
    MAX_RETRIES = 1

    # Paths
    BASE_DIR = Path(__file__).parent
    PROMPTS_DIR = BASE_DIR / "prompts"
    REPORTS_DIR = BASE_DIR / "reports"
    STORAGE_DIR = BASE_DIR / "storage"

    # Ensure directories exist
    REPORTS_DIR.mkdir(exist_ok=True)
    STORAGE_DIR.mkdir(exist_ok=True)


config = Config()
