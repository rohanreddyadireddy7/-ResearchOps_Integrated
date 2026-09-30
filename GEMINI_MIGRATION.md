# Migrating the earlier ResearchOps build from OpenAI to Gemini

This package is already converted. These notes are only for setup.

## 1. Stop the old backend

In the backend terminal press:

```text
Ctrl + C
```

## 2. Update `backend/.env`

Remove or ignore the old OpenAI settings:

```env
OPENAI_API_KEY=...
OPENAI_MODEL=...
```

Use:

```env
GEMINI_API_KEY=your_real_google_ai_studio_key
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_FALLBACK_MODELS=gemini-3.5-flash
GEMINI_MAX_RETRIES=1

TAVILY_API_KEY=your_real_tavily_key
HADOOP_MODE=local
RESEARCH_WORKERS=6
```

## 3. Restart backend

From the project root:

```powershell
.\run_backend.bat
```

The script runs `pip install -r backend/requirements.txt`, so the official `google-genai` package is installed automatically even if your existing virtual environment was created for the OpenAI build.

## 4. Confirm configuration

Open:

```text
http://127.0.0.1:8000/health
```

You want:

```json
"status": "ok",
"missing": [],
"llm_provider": "gemini"
```

## 5. Start/refresh frontend

If the frontend is not running:

```powershell
.\run_frontend.bat
```

Then open:

```text
http://localhost:8501
```

## First live run

Because Gemini's free tier has rate limits, start with:

- Research tasks: 3
- Sources per task: 2

After the full pipeline works, increase them gradually.
