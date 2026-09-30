# ResearchOps Architecture — Gemini Build

## End-to-end flow

```text
Streamlit UI
   |
   v
FastAPI /research
   |
   +--> Gemini Planner Agent -> independent tasks
   |
   +--> Parallel Tavily searches -> source documents + URLs
   |
   +--> MapReduce layer
   |      |- Local parallel MapReduce for VS Code/laptop development
   |      `- Hadoop Streaming mapper/reducer when configured
   |
   +--> Gemini Evidence Agent -> claims bound to source IDs
   |
   +--> Gemini Evidence Verifier -> supported / contradicted / uncertain
   |
   +--> Corroboration gate -> 2 independent domains OR authoritative primary source
   |
   +--> Gemini Synthesis Agent -> findings, opportunities, risks, mitigations
   |
   +--> Forecast Service -> evidence scenarios OR ML trend model
   |
   +--> Risk Service -> 1-5 matrix + Monte Carlo impact index
   |
   `--> SQLite -> job state + final JSON/Markdown report
```

## Scaling boundary

The laptop build separates deterministic high-volume processing from LLM processing. Raw research text can scale horizontally through Hadoop Streaming. Gemini receives selected source excerpts and reduced evidence rather than every raw token. For production, replace the in-process job executor with a distributed queue and SQLite with PostgreSQL while keeping the API contract and agents unchanged.

## Evidence model

Each retrieved source receives `S1`, `S2`, etc. Claims can only reference those IDs. A second Gemini pass checks whether the supplied excerpt actually entails each claim. The final verification gate accepts a supported claim when:

- two or more independent source domains support it; or
- a high-authority primary source supports it.

This is evidence verification, not a guarantee that a web source is objectively correct.

## Forecast model

- If the user supplies at least four historical year/value observations, Ridge regression is fit to log-values and used for a five-year trend projection with simulated uncertainty bands.
- Otherwise, explicit growth/CAGR percentages found in verified evidence are used for downside/base/upside scenarios.
- If neither exists, no numeric forecast is fabricated.

## Hadoop files

- `backend/app/mapreduce/mapper.py`
- `backend/app/mapreduce/reducer.py`
- `backend/app/mapreduce/hadoop_engine.py`

The Hadoop engine uploads JSONL documents to HDFS, executes Streaming, and reads reducer output back into the research pipeline.
