# Smart Travel & Weather Planning Agent

Python app that coordinates **three CrewAI agents** (Weather, Budget, Travel Planner) backed by **LangChain ChatGroq** and live **OpenWeatherMap** forecasts. The final brief is a single markdown document with itinerary, budget estimates, weather guidance, and packing ideas.

## Features

- **Weather agent**: OpenWeatherMap 5-day / 3-hour forecast (aggregated per day), tool access for refreshes or other cities, best-date suggestions, activity and packing guidance.
- **Budget agent**: Estimated lodging, food, local transport, and activities, aligned with the user’s budget string and trip length (clearly labeled as **approximations**).
- **Travel planner agent**: Day-wise itinerary with timings, sights, and dining ideas; final task merges everything into a fixed section layout.

## Prerequisites

- Python **3.10+**
- [Groq API key](https://console.groq.com/keys)
- [OpenWeatherMap API key](https://home.openweathermap.org/api_keys)

## Setup

```bash
cd "smart travel agent"
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt