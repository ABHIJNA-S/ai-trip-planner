import os
from typing import List, Dict

import requests
from langchain_core.tools import tool


OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"


@tool
def get_current_weather(city: str) -> str:
    """
    Get the current weather and a short forecast for the given city
    using the OpenWeather API.

    Returns a human-readable summary string. If the API key is missing
    or the request fails, returns a descriptive message instead of
    raising an error (so the agent can gracefully handle it).
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return (
            "Real-time weather is unavailable because OPENWEATHER_API_KEY "
            "is not set. You may still provide general, non-real-time "
            "weather expectations for the season."
        )

    try:
        # Current weather
        current_resp = requests.get(
            f"{OPENWEATHER_BASE_URL}/weather",
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=10,
        )
        current_resp.raise_for_status()
        current = current_resp.json()

        # Short forecast (next ~24 hours)
        forecast_resp = requests.get(
            f"{OPENWEATHER_BASE_URL}/forecast",
            params={
                "q": city,
                "appid": api_key,
                "units": "metric",
                "cnt": 8,  # roughly 24 hours (3h steps)
            },
            timeout=10,
        )
        forecast_resp.raise_for_status()
        forecast = forecast_resp.json()

        description = current["weather"][0]["description"].capitalize()
        temp = current["main"]["temp"]
        feels_like = current["main"]["feels_like"]

        forecasts: List[Dict] = []
        for item in forecast.get("list", []):
            forecasts.append(
                {
                    "time": item.get("dt_txt"),
                    "temp": item.get("main", {}).get("temp"),
                    "description": item.get("weather", [{}])[0].get(
                        "description", ""
                    ),
                }
            )

        summary_lines = [
            f"Current weather in {city}: {description}, {temp:.1f}°C (feels like {feels_like:.1f}°C).",
            "Short-term forecast (next ~24 hours):",
        ]

        for f in forecasts:
            if not f["time"]:
                continue
            summary_lines.append(
                f"- {f['time']}: {f['temp']:.1f}°C, {f['description']}"
            )

        return "\n".join(summary_lines)

    except Exception as e:
        return (
            "Could not fetch real-time weather data from OpenWeather. "
            f"Reason: {e}. You may still provide general guidance based on the "
            "typical climate of the destination."
        )


@tool
def get_dummy_flight_options(city: str) -> List[Dict]:
    """
    Return a few dummy flight options for the given destination city.

    In a real application you would replace this with calls to a flight
    search API. For now we return simple example data that the agent
    can present to the user.
    """
    return [
        {
            "airline": "Example Air",
            "from": "Your Home City",
            "to": city,
            "stops": 0,
            "duration_hours": 7,
            "price_usd": 650,
            "notes": "Morning non-stop flight with a meal included.",
        },
        {
            "airline": "Sample Airlines",
            "from": "Your Home City",
            "to": city,
            "stops": 1,
            "duration_hours": 10,
            "price_usd": 520,
            "notes": "One layover, budget-friendly option.",
        },
        {
            "airline": "Budget Wings",
            "from": "Your Home City",
            "to": city,
            "stops": 2,
            "duration_hours": 13,
            "price_usd": 430,
            "notes": "Ultra-budget with basic amenities.",
        },
    ]


@tool
def get_dummy_hotel_options(city: str) -> List[Dict]:
    """
    Return a few dummy hotel options for the given destination city.

    In a real application you would replace this with calls to a hotel
    search API. For now we return simple example data that the agent
    can present to the user.
    """
    return [
        {
            "name": f"{city} Central Comfort Hotel",
            "stars": 3,
            "price_per_night_usd": 90,
            "location": "Central area, good public transport",
            "notes": "Great value, basic but clean rooms.",
        },
        {
            "name": f"{city} Riverside Boutique",
            "stars": 4,
            "price_per_night_usd": 150,
            "location": "Scenic neighborhood near main attractions",
            "notes": "Stylish boutique hotel with breakfast included.",
        },
        {
            "name": f"Luxury Grand {city}",
            "stars": 5,
            "price_per_night_usd": 260,
            "location": "Premium district",
            "notes": "High-end amenities, spa, and concierge services.",
        },
    ]

