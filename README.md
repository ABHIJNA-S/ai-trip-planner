## AI Trip Planner (Streamlit + LangChain + Gemini)

An end-to-end **AI Trip Planner** web app built with:

- **Streamlit** for the user interface
- **LangChain** agent architecture
- **Gemini (Google Generative AI)** as the LLM
- **OpenWeather API** for real-time weather (optional but recommended)
- **Dummy flight and hotel tools** when real APIs are not available

The app lets a user enter:

- A **destination city**
- The **number of days** for the trip

and then generates:

1. One paragraph about the **cultural & historical importance** of the city  
2. **Current weather** and a short forecast  
3. **Suggested travel dates** (best time to visit)  
4. **Flight options** (dummy data)  
5. **Hotel options** (dummy data)  
6. A **day-wise itinerary**

All of this is orchestrated by a **LangChain agent** using tools.

---

### Project structure

- `app.py` – Streamlit UI entry point (`streamlit run app.py`)
- `agent.py` – LangChain agent setup and helper to plan a trip
- `tools.py` – Weather, dummy flight, and dummy hotel tools
- `requirements.txt` – Python dependencies
- `.env.example` – Example environment file with API keys

You should create your own `.env` file (see below).

---

### 1. Installation

1. **Create and activate a virtual environment** (optional but recommended):

   ```bash
   # From inside the project folder
   python -m venv .venv
   .venv\Scripts\activate  # Windows PowerShell
   # source .venv/bin/activate  # macOS / Linux
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

---

### 2. Configure API keys (`.env`)

1. Copy the example file:

   ```bash
   copy .env.example .env  # PowerShell / CMD on Windows
   # or
   # cp .env.example .env  # macOS / Linux
   ```

2. Open `.env` in a text editor and fill in:

   ```text
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   ```

   - `GOOGLE_API_KEY` is **required** for Gemini.
   - `OPENWEATHER_API_KEY` is **optional**; if missing, the app will still run,
     but weather will be generic instead of real-time.

The app uses `python-dotenv` to load these values when `app.py` starts.

---

### 3. Run the app

From the project directory, run:

```bash
streamlit run app.py
```

Your browser should open automatically at a URL like:

```text
http://localhost:8501
```

If not, copy the URL printed in the terminal and open it manually.

---

### 4. How it works (high level)

- **Streamlit UI (`app.py`)**
  - Collects the destination city and number of days.
  - Initializes the LangChain agent.
  - Calls the `plan_trip(...)` helper, then renders the returned JSON into sections.

- **LangChain Agent (`agent.py`)**
  - Uses `ChatGoogleGenerativeAI` (Gemini) as the LLM.
  - Uses a system prompt that:
    - Explains the available tools (weather, flights, hotels).
    - Asks the model to return a **single JSON object** with all required fields.
  - Calls tools via `create_tool_calling_agent` + `AgentExecutor`.

- **Tools (`tools.py`)**
  - `get_current_weather(city)` – uses **OpenWeather** to fetch:
    - Current weather
    - A short-term forecast (approx. next 24 hours)
    - If the API key is missing or a request fails, it returns a friendly text message.
  - `get_dummy_flight_options(city)` – returns a list of example flight options.
  - `get_dummy_hotel_options(city)` – returns a list of example hotel options.

---

### 5. Error handling

- If `GOOGLE_API_KEY` is missing, the Streamlit app:
  - Shows an error message in the UI.
  - Avoids crashing by not calling the agent.

- If `OPENWEATHER_API_KEY` is missing:
  - A warning is shown.
  - The weather tool returns a text message explaining that real-time weather is unavailable.

- If the LLM returns invalid JSON:
  - The app shows a basic error message.
  - It also displays the **raw model output** in a collapsible section for debugging.

---

### 6. Customization ideas

- Replace the dummy flight and hotel tools with real APIs.
- Add user controls for:
  - Budget level
  - Travel month/season
  - Preferred activities (museums, nightlife, nature, etc.)
- Store itineraries for later viewing (e.g., in a database).

This project is intended as a **beginner-friendly starting point** for building
your own AI-powered travel applications with Streamlit and LangChain.

