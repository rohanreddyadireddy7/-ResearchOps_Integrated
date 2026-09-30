@echo off
setlocal
cd /d %~dp0\frontend
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
echo.
echo ResearchOps frontend will run on port 8501.
echo Desktop: http://localhost:8501
echo Android on the same Wi-Fi: use http://YOUR-PC-IP:8501
Echo Find your PC IPv4 address with: ipconfig
Echo.
streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --browser.gatherUsageStats false
