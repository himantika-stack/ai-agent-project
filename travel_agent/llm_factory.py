"""LangChain Groq LLM used by CrewAI agents."""

from __future__ import annotations

from langchain_groq import ChatGroq

from travel_agent.config import Settings


def build_llm(settings: Settings) -> ChatGroq:
    if not settings.groq_api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. Add it to your environment or .env file."
        )
    return ChatGroq(
        model=settings.groq_model,
        temperature=0.35,
        groq_api_key=settings.groq_api_key,
    )
