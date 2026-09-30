@echo off
setlocal
cd /d %~dp0\backend

if not exist .env (
  copy /Y .env.example .env >nul
  echo.
  echo Created backend\.env from .env.example.
  echo Add your GEMINI_API_KEY and TAVILY_API_KEY, save the file, then run this script again.
  echo.
  pause
  exit /b 1
)

if not exist .venv (
  py -3.11 -m venv .venv
)
call .venv\Scripts\activate
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Dependency installation failed. Review the pip error above.
  pause
  exit /b 1
)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
