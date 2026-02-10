import os
from typing import Any, Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tools import get_current_weather, get_dummy_flight_options, get_dummy_hotel_options


def _build_prompt() -> ChatPromptTemplate:
    """
    Build the system + user prompt for the trip planner agent.

    The agent is instructed to ALWAYS call tools for weather, flights,
    and hotels when possible, and then return a single JSON object
    with the fields needed by the Streamlit UI.
    """
    system_message = (
        "You are an AI Trip Planner that creates clear, friendly itineraries.\n\n"
        "TOOLS AVAILABLE:\n"
        "- get_current_weather(city): returns real-time weather summary (or an explanation if the API key is missing).\n"
        "- get_dummy_flight_options(city): returns example flight options.\n"
        "- get_dummy_hotel_options(city): returns example hotel options.\n\n"
        "RESPONSE FORMAT:\n"
        "After using tools as needed, your FINAL answer must be a single valid JSON object.\n"
        "Do NOT wrap it in markdown or backticks.\n"
        "The JSON must have exactly these top-level keys:\n"
        "1. city_overview (string): one paragraph about the cultural and historical importance of the city.\n"
        "2. weather_summary (string): concise description of the current weather and short forecast, based primarily on tool output.\n"
        "3. suggested_dates (string): suggested best dates or seasons for travel, with a brief justification.\n"
        "4. flight_options (array of objects): each with keys airline, from, to, stops, duration_hours, price_usd, notes.\n"
        "5. hotel_options (array of objects): each with keys name, stars, price_per_night_usd, location, notes.\n"
        "6. itinerary (array of objects): a day-wise itinerary where each item has:\n"
        "   - day (integer day number starting at 1)\n"
        "   - title (short string)\n"
        "   - description (1–3 sentence description of activities for that day).\n\n"
        "IMPORTANT JSON RULES:\n"
        "- Use only double quotes (\") for JSON strings.\n"
        "- Do NOT include comments.\n"
        "- Ensure the JSON is syntactically valid so it can be parsed directly.\n"
    )

    return ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            # 'input' will be a natural language description of the user's request.
            ("human", "{input}"),
            # Scratchpad where the agent will record tool calls & intermediate steps.
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )


def create_trip_planner_agent() -> AgentExecutor:
    """
    Create and configure the LangChain agent used by the Streamlit app.

    This function initializes:
    - The Gemini chat model (via langchain-google-genai)
    - The tools (weather, dummy flights, dummy hotels)
    - The prompt that describes the desired JSON output format
    - An AgentExecutor that the UI can call with a simple text 'input'
    """
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        # We don't raise here so that the Streamlit app can perform its
        # own friendly error handling. Instead we surface a clear message.
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Please create a .env file "
            "with your Gemini API key."
        )

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.0-pro",
        temperature=0.7,
        max_output_tokens=2048,
        # The library will read GOOGLE_API_KEY from the environment.
    )

    tools = [get_current_weather, get_dummy_flight_options, get_dummy_hotel_options]
    prompt = _build_prompt()

    # create_tool_calling_agent configures an agent that knows how to
    # call tools using the model's built-in function/tool-calling API.
    agent = create_tool_calling_agent(llm, tools, prompt)

    # AgentExecutor provides a simple .invoke() interface that the UI
    # can call with {"input": "Plan a trip ..."}.
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return executor


def plan_trip(agent: AgentExecutor, city: str, num_days: int) -> Dict[str, Any]:
    """
    High-level helper used by the Streamlit app.

    It sends a natural language instruction to the agent and parses the
    JSON object returned in the final answer.
    """
    import json

    user_request = (
        f"Plan a {num_days}-day trip to {city}. "
        "Use tools to get real-time weather (if available) and example "
        "flight and hotel options. Then follow the RESPONSE FORMAT "
        "specified in the system message and return only the JSON object."
    )

    result = agent.invoke({"input": user_request})
    output_text = result.get("output", "").strip()

    # Attempt to parse the agent's JSON response safely.
    try:
        parsed = json.loads(output_text)
    except json.JSONDecodeError:
        # If parsing fails, return a simple structure that the UI can show.
        parsed = {
            "city_overview": "There was an error parsing the AI's response. "
            "Below is the raw text output.",
            "weather_summary": "",
            "suggested_dates": "",
            "flight_options": [],
            "hotel_options": [],
            "itinerary": [],
            "raw_output": output_text,
        }

    return parsed



