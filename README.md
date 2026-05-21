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
copy .env.example .env          # Windows — then edit .env
# cp .env.example .env          # Unix
```

Fill in `GROQ_API_KEY` and `OPENWEATHER_API_KEY` in `.env`.

Optional environment variables:

| Variable | Purpose |
|----------|---------|
| `GROQ_MODEL` | Defaults to `llama-3.3-70b-versatile` |
| `OPENWEATHER_UNITS` | `metric` (default) or `imperial` |

## Run (Streamlit)

```bash
streamlit run streamlit_app.py
```

## Run (CLI)

```bash
python cli.py --source "Delhi, IN" --destination "Manali, IN" --budget "₹20,000" --days 4 --preferences "adventure, hiking"
```

## Project layout

| Path | Role |
|------|------|
| `travel_agent/config.py` | Environment-backed settings |
| `travel_agent/services/openweather.py` | OpenWeatherMap client + daily aggregates |
| `travel_agent/tools/weather_tools.py` | LangChain tool wrapping the client (CrewAI-compatible) |
| `travel_agent/llm_factory.py` | LangChain `ChatGroq` factory |
| `travel_agent/agents.py` | CrewAI agent definitions |
| `travel_agent/tasks.py` | CrewAI tasks + context chain |
| `travel_agent/crew.py` | Sequential `Crew` assembly |
| `travel_agent/runner.py` | Prefetch weather, kickoff crew, return text |
| `streamlit_app.py` | Web UI |
| `cli.py` | Command-line entry |

## Output format

The crew’s final task emits markdown with these sections:

1. Destination Overview  
2. Weather Forecast  
3. Estimated Budget  
4. Best Time to Visit  
5. Day-wise Travel Plan  
6. Packing List  
7. Travel Tips  

## Notes

- Budget figures are **LLM estimates**, not live quotes. Use them for planning bands, not binding prices.
- OpenWeatherMap **free** tier exposes the 2.5 **forecast** endpoint used here (~5 days of 3-hour steps).
- If the source city forecast fails, the runner continues with a stub message so the crew can still plan the destination.

## License

Use and modify freely for your own projects.
