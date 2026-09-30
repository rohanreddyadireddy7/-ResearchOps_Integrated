#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/frontend"
python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --browser.gatherUsageStats false
