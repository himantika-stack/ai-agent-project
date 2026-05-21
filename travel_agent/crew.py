"""Assemble the CrewAI crew (sequential multi-agent workflow)."""

from __future__ import annotations

from typing import Iterable

from crewai import Crew, Process


def create_crew(agents: Iterable, tasks: Iterable) -> Crew:
    """Build a sequential crew: Weather → Budget → Itinerary → Final brief."""
    return Crew(
        agents=list(agents),
        tasks=list(tasks),
        process=Process.sequential,
        verbose=False,
    )
