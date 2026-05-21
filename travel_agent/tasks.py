"""CrewAI task definitions for the travel crew."""

from __future__ import annotations

from crewai import Task

from travel_agent.agents import build_agents
from travel_agent.models import TripInput


def build_tasks(
    trip: TripInput,
    weather_agent,
    budget_agent,
    travel_planner_agent,
    prefetched_destination_weather: str,
    prefetched_source_weather: str,
) -> tuple[Task, Task, Task, Task]:
    base_ctx = trip.summary()

    weather_task = Task(
        description=(
            f"{base_ctx}\n"
            "API snapshot for DESTINATION (ground truth — reconcile with tool data if needed):\n"
            f"{prefetched_destination_weather}\n\n"
            "API snapshot for SOURCE (outbound context):\n"
            f"{prefetched_source_weather}\n\n"
            "Optionally call `openweather_forecast` again if you need a sharper query string, "
            "but do not contradict the snapshots unless the tool returns newer conflicting data.\n"
            "Deliver: best candidate travel dates inside the forecast window, rain/comfort notes, "
            "weather-friendly activities, and a packing list tailored to conditions and preferences."
        ),
        expected_output=(
            "A structured section titled 'Weather Forecast' plus 'Best Time to Visit' bullets, "
            "'Weather-friendly activities', and 'Packing list' — concise but actionable."
        ),
        agent=weather_agent,
    )

    budget_task = Task(
        description=(
            f"{base_ctx}\n"
            "Use the weather team's conclusions (temperature bands, rain risk) to sanity-check "
            "activity choices and incidental costs (gear rental, indoor backup options, etc.).\n"
            "Build an estimated budget in the user's currency context as implied by their budget "
            "string. Include subtotals: lodging, food, local transport, activities/misc, and a "
            "buffer. Call out budget-friendly swaps. Total must be discussed relative to their cap."
        ),
        expected_output=(
            "Section 'Estimated Budget' with line items and a total range; note what to cut if "
            "over budget."
        ),
        agent=budget_agent,
        context=[weather_task],
    )

    itinerary_task = Task(
        description=(
            f"{base_ctx}\n"
            "Create a day-by-day plan for exactly the stated number of days. Each day: morning / "
            "afternoon / evening blocks, suggested visit durations, one or two dining ideas, and "
            "logistics tips. Respect weather (e.g. rainy-day alternates) and keep spend tone "
            "aligned with the budget analysis."
        ),
        expected_output=(
            "Section 'Day-wise Travel Plan' with clear Day 1…Day N headings and timing hints."
        ),
        agent=travel_planner_agent,
        context=[weather_task, budget_task],
    )

    final_task = Task(
        description=(
            "Consolidate ALL prior agent outputs into one cohesive travel brief for the user.\n"
            f"{base_ctx}\n"
            "The final answer MUST use this exact section order and headings (markdown `##`):\n"
            "## Destination Overview\n"
            "## Weather Forecast\n"
            "## Estimated Budget\n"
            "## Best Time to Visit\n"
            "## Day-wise Travel Plan\n"
            "## Packing List\n"
            "## Travel Tips\n"
            "Do not omit sections. Keep tone practical and specific to the destination and preferences."
        ),
        expected_output="A single markdown document with the seven sections above, fully filled.",
        agent=travel_planner_agent,
        context=[weather_task, budget_task, itinerary_task],
    )

    return weather_task, budget_task, itinerary_task, final_task


def build_tasks_for_crew(
    trip: TripInput,
    prefetched_destination_weather: str,
    prefetched_source_weather: str,
    llm,
    weather_tools: list,
) -> tuple[tuple, tuple]:
    """Return (agents_tuple, tasks_tuple) ready for Crew construction."""
    w_agent, b_agent, t_agent = build_agents(llm, weather_tools)
    tasks = build_tasks(
        trip,
        w_agent,
        b_agent,
        t_agent,
        prefetched_destination_weather,
        prefetched_source_weather,
    )
    return (w_agent, b_agent, t_agent), tasks
