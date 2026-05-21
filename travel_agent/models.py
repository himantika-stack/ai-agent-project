"""Trip input model shared by CLI and Streamlit."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TripInput:
    source: str
    destination: str
    budget: str
    days: int
    travel_preferences: str

    def summary(self) -> str:
        return (
            f"Source: {self.source}\n"
            f"Destination: {self.destination}\n"
            f"Budget: {self.budget}\n"
            f"Number of days: {self.days}\n"
            f"Travel preferences / type: {self.travel_preferences}\n"
        )
