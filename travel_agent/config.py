"""Load configuration and API keys from environment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    """Application settings sourced from environment variables."""

    groq_api_key: Optional[str]
    openweather_api_key: Optional[str]
    groq_model: str
    openweather_units: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            openweather_api_key=os.getenv("OPENWEATHER_API_KEY"),
            groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            openweather_units=os.getenv("OPENWEATHER_UNITS", "metric"),
        )


def get_settings() -> Settings:
    return Settings.from_env()
