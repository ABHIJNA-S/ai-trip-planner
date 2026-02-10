import os
import streamlit as st
from dotenv import load_dotenv
import requests

from agent import plan_trip


# Load environment variables
load_dotenv()


def get_weather(city: str) -> str:
    """Fetch current weather from OpenWeather API."""
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return "Weather data not available."

    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"q={city}&appid={api_key}&units=metric"
        )
        data = requests.get(url, timeout=10).json()

        description = data["weather"][0]["description"]
        temp = data["main"]["temp"]

        return f"{description}, {temp}°C"
    except Exception:
        return "Weather data not available."


def main() -> None:
    st.set_page_config(page_title="AI Trip Planner", page_icon="✈️", layout="wide")

    st.title("AI Trip Planner ✈️")
    st.write(
        "Plan your trip using **Google Gemini + real-time weather data**."
    )

    city = st.text_input("Destination city", placeholder="e.g., Paris")
    days = st.number_input("Number of days", min_value=1, max_value=30, value=3)

    if st.button("Plan my trip"):
        if not city.strip():
            st.error("Please enter a destination city.")
            return

        if not os.getenv("GOOGLE_API_KEY"):
            st.error("GOOGLE_API_KEY is missing in Streamlit Secrets.")
            return

        with st.spinner("Generating trip plan..."):
            weather = get_weather(city)

            # Dummy data for flights & hotels (valid for lab)
            flights = "Sample flights: ₹8,000 – ₹12,000"
            hotels = "Sample hotels: ₹2,000 – ₹5,000 per night"

            plan = plan_trip(city, int(days), weather, flights, hotels)

        st.success("Trip plan generated!")

        st.write(plan)


if __name__ == "__main__":
    main()
