# ResearchOps — Gemini + Tavily Research AI Agent

This is the Gemini-enabled build of ResearchOps. It uses **Google Gemini** for planning, claim extraction, evidence verification and report synthesis, **Tavily** for web research, and the included **MapReduce layer** for scalable text aggregation.

## What it does

1. Accepts a business/research problem statement.
2. Uses Gemini to decompose it into independent research tasks.
3. Searches the web through Tavily in parallel.
4. Runs text aggregation using the MapReduce pattern. In development it uses the included local parallel engine; if Hadoop Streaming is configured it can run the supplied Hadoop mapper/reducer.
5. Extracts factual claims only from retrieved excerpts.
6. Verifies those claims against the excerpts and keeps only claims corroborated by at least two independent domains or one high-authority primary source.
7. Synthesizes verified findings into opportunities, risks, mitigations and decision questions.
8. Runs reproducible risk scoring/Monte Carlo analysis.
9. Produces either an evidence-based 5-year scenario forecast, or a trained Ridge log-trend forecast when at least four user-supplied historical points are available.
10. Generates a Markdown report with source links directly under evidence-backed information.

> “Verified” means supported by retrieved evidence under this system's rules. It is not a guarantee of absolute truth.

## Folder structure

```text
ResearchOps_Integrated/
  backend/
    app/
      agents/          planner, evidence extraction/verification, synthesis
      analytics/       forecasting and risk simulation
      core/            configuration
      mapreduce/       local engine + Hadoop Streaming mapper/reducer
      models/          API schemas
      services/        Gemini and Tavily clients
      storage/         SQLite job/result storage
      main.py          FastAPI application
      orchestrator.py  end-to-end research pipeline
    .env.example
    requirements.txt
  frontend/
    app.py              Streamlit UI connected to FastAPI
    requirements.txt
  run_backend.bat / .sh
  run_frontend.bat / .sh
  GEMINI_MIGRATION.md
```

## Windows / VS Code — quickest setup

### 1. Open the folder

Open `ResearchOps_Integrated` in VS Code.

### 2. Create `backend/.env`

Copy:

```text
backend/.env.example
```

to:

```text
backend/.env
```

Then enter your real keys:

```env
GEMINI_API_KEY=your_real_google_ai_studio_key
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_FALLBACK_MODELS=gemini-3.5-flash
GEMINI_MAX_RETRIES=1

TAVILY_API_KEY=your_real_tavily_key

HADOOP_MODE=local
RESEARCH_WORKERS=6
```

Do not put your API keys in GitHub or send them in chat.

### 3. Start the backend

Terminal 1, from the project root:

```bat
.\run_backend.bat
```

The script creates/uses `backend/.venv`, installs dependencies including `google-genai`, and starts FastAPI.

Wait for:

```text
Application startup complete.
```

Check:

```text
http://127.0.0.1:8000/health
```

A ready configuration should show approximately:

```json
{
  "status": "ok",
  "missing": [],
  "llm_provider": "gemini",
  "mapreduce_engine": "local-mapreduce",
  "model": "gemini-3.5-flash-lite"
}
```

### 4. Start the frontend

Terminal 2, from the project root:

```bat
.\run_frontend.bat
```

Open:

```text
http://localhost:8501
```

## If you already had the OpenAI version

You do **not** need an OpenAI API key in this build. Replace the old `.env` values with `GEMINI_API_KEY` and `TAVILY_API_KEY`, then restart the backend. See `GEMINI_MIGRATION.md`.

## Gemini model configuration

The default is:

```env
GEMINI_MODEL=gemini-3.5-flash-lite
```

The model is deliberately configurable because availability and free-tier quotas can differ by account/project. An optional fallback is configured with:

```env
GEMINI_FALLBACK_MODELS=gemini-3.5-flash
```

If Google reports that a model is unavailable to your project, change these values to a model shown as available in your Google AI Studio project.

## Hadoop MapReduce modes

For normal VS Code use, keep:

```env
HADOOP_MODE=local
```

- `local`: runs the map/reduce logic with a local Python worker pool. Best for laptop/VS Code development.
- `auto`: uses Hadoop Streaming when Hadoop and the streaming JAR are configured; otherwise falls back to local mode.
- `streaming`: requires Hadoop and fails if it is not configured.

Example for a Hadoop installation:

```env
HADOOP_MODE=streaming
HADOOP_BINARY=hadoop
HADOOP_STREAMING_JAR=C:/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.x.x.jar
```

The backend writes research documents as JSONL, uploads them to HDFS under `/researchops/<research-id>/input`, runs `mapper.py` and `reducer.py`, then reads the reduced output back into the research pipeline.

### Why Gemini is not called inside every Hadoop mapper

Calling an external LLM from millions of mapper records is slow, quota-intensive and unreliable. Hadoop handles deterministic high-volume aggregation; Gemini operates on selected task-level evidence afterward.

## Forecasting behavior

### Without historical data
The system searches verified findings for explicit growth/CAGR values. If it finds them, it builds downside/base/upside 5-year scenarios. If no defensible numeric growth evidence exists, it returns insufficient evidence instead of inventing a forecast.

### With historical data
Provide at least four year/value rows in the frontend. The backend trains Ridge regression on log values, reports in-sample R², forecasts five years and uses simulation to produce P10/P90 bands.

## Common errors

### `Missing: GEMINI_API_KEY`
Add `GEMINI_API_KEY=...` to `backend/.env`, save, stop the backend with `Ctrl+C`, then run `run_backend.bat` again.

### Gemini authentication error
Make sure the key is from Google AI Studio and that you edited `backend/.env`, not only `.env.example`.

### Gemini quota/rate-limit error
The free tier has quotas. Reduce `Research tasks` and `Sources per task`, wait for the quota window to reset, or select another model available to your project.

### `Missing: TAVILY_API_KEY`
Add your Tavily key to `backend/.env` and restart the backend.

## API endpoints

- `GET /health`
- `POST /research`
- `GET /research/{research_id}`
- `GET /research/{research_id}/report`

---

## v1.2 Responsive Decision Workspace

This build adds a formal light UI with black text, responsive desktop/mobile behavior, a selectable 1-5 year forecast horizon, optional evidence-grounded AI decision suggestions, research-quality indicators, richer risk/forecast visualizations, and downloadable PDF reports with charts.

### Run on Windows

1. Copy `backend/.env.example` to `backend/.env` and add `GEMINI_API_KEY` and `TAVILY_API_KEY`.
2. From the project root run `run_backend.bat` in Terminal 1.
3. Run `run_frontend.bat` in Terminal 2.
4. Desktop: open `http://localhost:8501`.
5. Backend status: open `http://127.0.0.1:8000/health`.

### Open on Android on the same local network

The Windows frontend launcher binds Streamlit to all local interfaces. Run `ipconfig` on the Windows PC, note the Wi-Fi/Ethernet IPv4 address, and open `http://<PC-IP>:8501` on the Android device connected to the same Wi-Fi. If Windows Firewall prompts, allow Python/Streamlit on private networks only.

### Report downloads

- Markdown: portable, source-linked research record.
- PDF: executive report with research-quality, risk, and forecast charts plus the source register.

See `DECISION_UI_UPGRADE.md` for the change summary and decision-support safeguards.
