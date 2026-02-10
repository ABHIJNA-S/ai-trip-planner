import os

import streamlit as st
from dotenv import load_dotenv

from agent import create_trip_planner_agent, plan_trip


# Load environment variables from a local .env file if present.
# This allows beginners to keep their API keys outside of the code.
load_dotenv()


def check_api_keys() -> None:
    """
    Perform basic checks for required API keys and show
    clear, beginner-friendly messages in the UI.
    """
    google_key = os.getenv("GOOGLE_API_KEY")
    openweather_key = os.getenv("OPENWEATHER_API_KEY")

    if not google_key:
        st.error(
            "GOOGLE_API_KEY is missing.\n\n"
            "Create a `.env` file (you can copy from `.env.example`) and add "
            "`GOOGLE_API_KEY=your_google_gemini_api_key_here`.\n"
            "Then restart the app."
        )

    if not openweather_key:
        st.warning(
            "OPENWEATHER_API_KEY is not set. The app will still work, but "
            "real-time weather will fall back to a generic description.\n\n"
            "To enable live weather, add "
            "`OPENWEATHER_API_KEY=your_openweather_api_key_here` to your `.env` file."
        )


def main() -> None:
    """
    Main entry point for the Streamlit web app.

    The layout is intentionally simple and beginner-friendly:
    - Users enter a destination city and number of days.
    - When they click the button, we call the LangChain agent.
    - The agent uses tools (weather, flights, hotels) and returns
      a structured JSON plan that we render as sections.
    """
    st.set_page_config(
        page_title="AI Trip Planner",
        page_icon="✈️",
        layout="wide",
    )

    st.title("AI Trip Planner ✈️")
    st.write(
        "Plan your next adventure with the help of **Gemini + LangChain**.\n\n"
        "Enter a city and how many days you want to stay, and the app will "
        "suggest flights, hotels, and a day-by-day itinerary."
    )

    check_api_keys()

    # Sidebar for settings / info
    with st.sidebar:
        st.header("How to use")
        st.markdown(
            "- Fill in the destination city.\n"
            "- Choose how many days to travel.\n"
            "- Click **Plan my trip**.\n\n"
            "Behind the scenes, a **LangChain agent** calls:\n"
            "- Gemini (Google Generative AI) for reasoning and planning\n"
            "- OpenWeather for real-time weather (if an API key is provided)\n"
            "- Dummy tools for flight and hotel suggestions"
        )

    # Main input form
    with st.form("trip_form"):
        city = st.text_input("Destination city", placeholder="e.g., Paris")
        num_days = st.number_input(
            "Number of days",
            min_value=1,
            max_value=30,
            step=1,
            value=5,
        )
        submitted = st.form_submit_button("Plan my trip")

    if submitted:
        if not city.strip():
            st.error("Please enter a destination city.")
            return

        if not os.getenv("GOOGLE_API_KEY"):
            # The check_api_keys() function already showed a message,
            # so we just return here to avoid a crash.
            return

        with st.spinner("Planning your trip with Gemini..."):
            try:
                agent = create_trip_planner_agent()
            except RuntimeError as e:
                st.error(str(e))
                return

            plan = plan_trip(agent, city.strip(), int(num_days))

        # Render the results in a clean, sectioned layout.
        st.success("Your trip plan is ready!")

        # Two-column layout for overview and weather.
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("1. City overview")
            st.write(plan.get("city_overview", "No overview available."))

        with col2:
            st.subheader("2. Current weather & short forecast")
            st.write(plan.get("weather_summary", "No weather information available."))

        st.subheader("3. Suggested travel dates")
        st.write(plan.get("suggested_dates", "No suggested dates available."))

        # Flight options table
        st.subheader("4. Example flight options")
        flights = plan.get("flight_options", [])
        if flights:
            # Streamlit can render a list of dicts as a table automatically.
            st.table(flights)
        else:
            st.write("No flight options were provided.")

        # Hotel options table
        st.subheader("5. Example hotel options")
        hotels = plan.get("hotel_options", [])
        if hotels:
            st.table(hotels)
        else:
            st.write("No hotel options were provided.")

        # Day-wise itinerary
        st.subheader("6. Day-wise itinerary")
        itinerary = plan.get("itinerary", [])

        if itinerary:
            for day in itinerary:
                day_num = day.get("day")
                title = day.get("title", f"Day {day_num}")
                description = day.get("description", "")

                with st.expander(f"Day {day_num}: {title}"):
                    st.write(description)
        else:
            st.write("No itinerary was generated.")

        # If parsing failed, we also show the raw model output for debugging.
        raw_output = plan.get("raw_output")
        if raw_output:
            st.markdown("---")
            st.subheader("Raw AI output (for debugging)")
            st.code(raw_output)


if __name__ == "__main__":
    # This allows the app to be run with:
    #   streamlit run app.py
    main()

