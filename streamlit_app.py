"""Streamlit UI for the Smart Travel & Weather Planning Agent."""

from __future__ import annotations

import streamlit as st

from travel_agent.models import TripInput
from travel_agent.runner import run_smart_trip

st.set_page_config(
    page_title="Smart Travel & Weather Agent",
    page_icon="🧭",
    layout="wide",
)

st.title("Smart Travel & Weather Planning Agent")
st.caption("CrewAI multi-agent crew · LangChain Groq · OpenWeatherMap live forecasts")

with st.sidebar:
    st.header("About")
    st.markdown(
        "Three collaborating agents — **Weather**, **Budget**, **Travel Planner** — "
        "produce a single markdown brief with itinerary, costs, and packing ideas."
    )
    st.markdown(
        "Set `GROQ_API_KEY` and `OPENWEATHER_API_KEY` in a `.env` file or your environment."
    )

col1, col2 = st.columns(2)
with col1:
    source = st.text_input("Source location", placeholder="e.g. Delhi, IN")
    destination = st.text_input("Destination", placeholder="e.g. Manali, IN")
    budget = st.text_input("Budget", placeholder="e.g. ₹20,000 or 500 EUR")
with col2:
    days = st.number_input("Number of days", min_value=1, max_value=21, value=4, step=1)
    preferences = st.text_area(
        "Travel preferences",
        placeholder="e.g. adventure, hiking, vegetarian food, mid-range stays",
        height=120,
    )

submitted = st.button("Generate travel plan", type="primary")

if submitted:
    if not source.strip() or not destination.strip() or not budget.strip():
        st.error("Please fill in source, destination, and budget.")
    else:
        trip = TripInput(
            source=source.strip(),
            destination=destination.strip(),
            budget=budget.strip(),
            days=int(days),
            travel_preferences=preferences.strip() or "general",
        )
        with st.spinner("Running multi-agent crew (weather → budget → itinerary → brief)…"):
            try:
                report = run_smart_trip(trip)
            except Exception as exc:  # noqa: BLE001
                st.error(f"Run failed: `{exc}`")
            else:
                st.success("Done.")
                st.markdown(report)
