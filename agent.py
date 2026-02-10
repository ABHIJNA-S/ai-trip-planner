import os
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash-002")


def plan_trip(city: str, days: int, weather: str, flights: str, hotels: str) -> str:
    prompt = f"""
    Plan a {days}-day trip to {city}.

    Include:
    - 1 paragraph about cultural & historical significance
    - Current weather: {weather}
    - Flight options: {flights}
    - Hotel options: {hotels}
    - Day-wise itinerary
    """

    response = model.generate_content(prompt)
    return response.text







