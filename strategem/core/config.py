"""Strategem Core - Configuration (Mechanical Only)"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration (mechanical only)"""

    # API Configuration
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv(
        "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
    )
    LLM_MODEL: str = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "8000"))

    # Retry configuration
    MAX_RETRIES: int = 1

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    PROMPTS_DIR: Path = BASE_DIR / "prompts"
    REPORTS_DIR: Path = BASE_DIR / "reports"
    STORAGE_DIR: Path = BASE_DIR / "storage"

    # Ensure directories exist
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure required directories exist (mechanical only)"""
        cls.REPORTS_DIR.mkdir(exist_ok=True)
        cls.STORAGE_DIR.mkdir(exist_ok=True)


# Singleton instance
config = Config()
config.ensure_directories()
