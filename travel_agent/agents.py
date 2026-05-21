"""CrewAI agent definitions."""

from __future__ import annotations

from typing import Any, Sequence

from crewai import Agent
from langchain_groq import ChatGroq


def build_agents(
    llm: ChatGroq,
    weather_tools: Sequence[Any],
) -> tuple[Agent, Agent, Agent]:
    weather_agent = Agent(
        role="Weather & Climate Specialist",
        goal=(
            "Use live OpenWeatherMap data to judge temperature, humidity, and rain risk; "
            "recommend the best travel dates; suggest weather-appropriate activities and packing."
        ),
        backstory=(
            "You are a meteorology-aware travel consultant. You never invent numeric weather "
            "values—when tools return data, you treat that text as ground truth and explain "
            "implications clearly for travelers."
        ),
        tools=list(weather_tools),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    budget_agent = Agent(
        role="Trip Budget Analyst",
        goal=(
            "Produce a realistic estimated cost breakdown (lodging, food, local transport, "
            "activities) that respects the user's stated budget and trip length."
        ),
        backstory=(
            "You estimate costs using general market knowledge and clearly label figures as "
            "approximations. You flag uncertainty, suggest money-saving levers, and ensure the "
            "sum is plausibly within budget or explain what to trim."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    travel_planner_agent = Agent(
        role="Senior Travel Itinerary Planner",
        goal=(
            "Design a day-wise itinerary with famous sights, sensible visit times, meal ideas, "
            "and routing notes aligned with weather and budget context."
        ),
        backstory=(
            "You are an experienced destination planner who balances pacing, opening hours, "
            "and weather. You optimize order of visits to reduce backtracking when possible."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    return weather_agent, budget_agent, travel_planner_agent
