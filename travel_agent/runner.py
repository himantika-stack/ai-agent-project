"""High-level orchestration: OpenWeather fetch + CrewAI kickoff."""

from __future__ import annotations

import logging
from typing import Any

from travel_agent.config import get_settings
from travel_agent.crew import create_crew
from travel_agent.llm_factory import build_llm
from travel_agent.models import TripInput
from travel_agent.services.openweather import OpenWeatherClient, WeatherError
from travel_agent.tasks import build_tasks_for_crew
from travel_agent.tools.weather_tools import make_weather_forecast_tool

logger = logging.getLogger(__name__)


def _crew_output_text(result: Any) -> str:
    raw = getattr(result, "raw", None)
    if raw:
        return str(raw)
    return str(result)


def run_smart_trip(trip: TripInput) -> str:
    """
    Validate configuration, prefetch weather snapshots, run the crew, return markdown text.

    Raises:
        ValueError: missing LLM key or invalid trip parameters.
        WeatherError: OpenWeather failures when prefetching.
    """
    if trip.days < 1 or trip.days > 21:
        raise ValueError("Number of days must be between 1 and 21.")

    settings = get_settings()
    llm = build_llm(settings)

    if not settings.openweather_api_key:
        raise ValueError(
            "OPENWEATHER_API_KEY is not set. Add it to your environment or .env file."
        )

    client = OpenWeatherClient(
        settings.openweather_api_key,
        units=settings.openweather_units,
    )
    weather_tool = make_weather_forecast_tool(client)

    try:
        dest_block = client.forecast_summary_for_llm(trip.destination)
    except WeatherError:
        logger.exception("Destination weather prefetch failed")
        raise

    try:
        src_block = client.forecast_summary_for_llm(trip.source)
    except WeatherError as exc:
        logger.warning("Source weather prefetch failed, using error stub: %s", exc)
        src_block = f"(Could not load source weather: {exc})"

    agents, tasks = build_tasks_for_crew(
        trip,
        prefetched_destination_weather=dest_block,
        prefetched_source_weather=src_block,
        llm=llm,
        weather_tools=[weather_tool],
    )

    crew = create_crew(agents=agents, tasks=tasks)
    try:
        result = crew.kickoff()
    except Exception:
        logger.exception("Crew kickoff failed")
        raise

    return _crew_output_text(result)
