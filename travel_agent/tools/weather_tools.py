"""LangChain tool wrapping OpenWeatherMap (usable by CrewAI agents)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_core.tools import StructuredTool

if TYPE_CHECKING:
    from travel_agent.services.openweather import OpenWeatherClient


def make_weather_forecast_tool(client: "OpenWeatherClient") -> StructuredTool:
    """Return a tool instance bound to the given OpenWeather client."""

    def openweather_forecast(city: str) -> str:
        """
        Fetch a multi-day OpenWeatherMap forecast summary for a place name.
        Pass a clear city string (e.g. 'Manali, IN' or 'Lyon, FR').
        """
        try:
            return client.forecast_summary_for_llm(city)
        except Exception as exc:  # noqa: BLE001
            return f"Weather tool error for {city!r}: {exc}"

    return StructuredTool.from_function(
        name="openweather_forecast",
        description=(
            "Fetches real OpenWeatherMap forecast aggregates (about 5 days of 3-hour samples) "
            "for any city. Use for destination, source, or stopovers when planning weather, "
            "dates, packing, or outdoor activities."
        ),
        func=openweather_forecast,
    )
