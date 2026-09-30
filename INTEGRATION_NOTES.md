# Integration Notes — Gemini Conversion

## Current AI/search stack

- **Gemini Developer API**: research planning, claim extraction, evidence verification and synthesis.
- **Tavily**: current web search and source excerpts.
- **Local MapReduce / Hadoop Streaming**: deterministic text aggregation.
- **scikit-learn + NumPy**: forecasting and risk simulation.
- **FastAPI + SQLite**: backend API/job persistence.
- **Streamlit**: frontend.

## Changes from the earlier OpenAI build

- Removed the OpenAI runtime dependency from the backend requirements.
- Added Google's official `google-genai` SDK.
- Replaced `OpenAIService` with `GeminiService`.
- Changed runtime configuration from `OPENAI_API_KEY` / `OPENAI_MODEL` to `GEMINI_API_KEY` / `GEMINI_MODEL`.
- Added configurable Gemini fallback models and a small retry layer for transient API errors.
- Added clearer Gemini authentication, quota and model-availability errors.
- Updated `/health` to report `llm_provider: gemini` and the configured Gemini model.
- Updated the Streamlit sidebar to display the active provider/model and missing configuration.
- Kept Tavily, MapReduce, evidence gates, risk analysis, forecasts and report output unchanged.

## Secret handling

No real Gemini or Tavily credentials are included in this ZIP. Put them only in `backend/.env`. The project `.gitignore` excludes `.env`.
