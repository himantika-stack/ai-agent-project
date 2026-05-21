"""Simple CLI for the Smart Travel & Weather Planning Agent."""

from __future__ import annotations

import argparse
import sys

from travel_agent.models import TripInput
from travel_agent.runner import run_smart_trip


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI Smart Travel & Weather Planning (CrewAI + Groq + OpenWeatherMap)."
    )
    parser.add_argument("--source", required=True, help="Starting location (city, region).")
    parser.add_argument("--destination", required=True, help="Trip destination.")
    parser.add_argument("--budget", required=True, help='Budget string, e.g. "₹20,000" or "800 USD".')
    parser.add_argument("--days", type=int, required=True, help="Trip length in days (1–21).")
    parser.add_argument(
        "--preferences",
        required=True,
        help="Travel style: adventure, luxury, family, solo, etc.",
    )
    args = parser.parse_args()

    trip = TripInput(
        source=args.source,
        destination=args.destination,
        budget=args.budget,
        days=args.days,
        travel_preferences=args.preferences,
    )
    try:
        report = run_smart_trip(trip)
    except Exception as exc:  # noqa: BLE001 — CLI surfaces any failure clearly
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(report)


if __name__ == "__main__":
    main()
