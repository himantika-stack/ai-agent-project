"""OpenWeatherMap API client (forecast + geocoding)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class WeatherError(Exception):
    """Raised when OpenWeatherMap returns an error or unexpected payload."""


@dataclass
class GeoResult:
    name: str
    country: str
    lat: float
    lon: float


class OpenWeatherClient:
    """Thin wrapper around OpenWeatherMap 2.5 forecast and Geo 1.0 APIs."""

    GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"
    FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

    def __init__(self, api_key: str, units: str = "metric") -> None:
        if not api_key:
            raise WeatherError("OpenWeatherMap API key is missing.")
        self._api_key = api_key
        self._units = units

    def _get(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        try:
            resp = requests.get(url, params=params, timeout=20)
        except requests.RequestException as exc:
            raise WeatherError(f"Weather request failed: {exc}") from exc
        if resp.status_code != 200:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise WeatherError(f"Weather API HTTP {resp.status_code}: {detail}")
        try:
            return resp.json()
        except ValueError as exc:
            raise WeatherError("Weather API returned invalid JSON.") from exc

    def geocode(self, query: str, limit: int = 1) -> GeoResult:
        data = self._get(
            self.GEO_URL,
            {"q": query.strip(), "limit": limit, "appid": self._api_key},
        )
        if not data:
            raise WeatherError(f"No geocoding results for: {query!r}")
        row = data[0]
        return GeoResult(
            name=row.get("name", query),
            country=row.get("country", ""),
            lat=float(row["lat"]),
            lon=float(row["lon"]),
        )

    def forecast_raw(self, city_query: str) -> dict[str, Any]:
        return self._get(
            self.FORECAST_URL,
            {"q": city_query.strip(), "appid": self._api_key, "units": self._units},
        )

    def forecast_summary_for_llm(self, city_query: str) -> str:
        """
        Aggregate 3-hour forecast slots into daily human-readable summaries
        for agent prompts.
        """
        raw = self.forecast_raw(city_query)
        city = raw.get("city", {})
        name = city.get("name", city_query)
        country = city.get("country", "")
        listings = raw.get("list") or []
        if not listings:
            raise WeatherError("Forecast response contained no data points.")

        by_day: dict[str, dict[str, Any]] = {}
        for slot in listings:
            dt_txt = slot.get("dt_txt", "")
            day_key = dt_txt.split(" ")[0] if " " in dt_txt else dt_txt[:10]
            if not day_key:
                continue
            main = slot.get("main", {})
            weather = (slot.get("weather") or [{}])[0]
            pop = float(slot.get("pop", 0) or 0)
            entry = by_day.setdefault(
                day_key,
                {
                    "temps": [],
                    "humidity": [],
                    "pops": [],
                    "descriptions": [],
                    "wind_speeds": [],
                },
            )
            if "temp" in main:
                entry["temps"].append(float(main["temp"]))
            if "humidity" in main:
                entry["humidity"].append(float(main["humidity"]))
            entry["pops"].append(pop)
            desc = weather.get("description")
            if desc:
                entry["descriptions"].append(desc)
            wind = (slot.get("wind") or {}).get("speed")
            if wind is not None:
                entry["wind_speeds"].append(float(wind))

        lines = [
            f"Location resolved: {name}, {country} (query: {city_query}).",
            f"Units: {self._units}.",
            "Daily aggregates (from 3-hour forecast samples):",
        ]
        for day in sorted(by_day.keys()):
            e = by_day[day]
            temps = e["temps"]
            humidity = e["humidity"]
            pops = e["pops"]
            winds = e["wind_speeds"]
            descs = e["descriptions"]
            t_min = min(temps) if temps else None
            t_max = max(temps) if temps else None
            h_avg = sum(humidity) / len(humidity) if humidity else None
            pop_max = max(pops) if pops else 0.0
            wind_avg = sum(winds) / len(winds) if winds else None
            top_desc = max(set(descs), key=descs.count) if descs else "n/a"
            wind_txt = (
                f"{wind_avg:.1f} m/s"
                if wind_avg is not None
                else "n/a"
            )
            if t_min is not None and t_max is not None and h_avg is not None:
                lines.append(
                    f"- {day}: temp range {t_min:.1f}–{t_max:.1f}°, conditions ~{top_desc}, "
                    f"max rain probability ~{pop_max * 100:.0f}%, avg humidity ~{h_avg:.0f}%, "
                    f"avg wind ~{wind_txt}."
                )
            else:
                lines.append(
                    f"- {day}: {top_desc}, rain prob up to ~{pop_max * 100:.0f}%."
                )
        lines.append(
            "\nUse these aggregates as ground truth. Suggest best dates within this window "
            "and practical packing and activities aligned with the user preferences."
        )
        return "\n".join(lines)
