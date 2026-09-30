# ResearchOps Decision UI Upgrade

This build extends the Gemini + Tavily research agent with a formal responsive decision workspace.

## Added

- Black-first text system on light backgrounds for readability.
- Responsive layout for Windows desktop/laptop and Android/mobile browsers.
- 1-5 year forecast horizon selector passed through the API to both scenario and ML forecasting.
- Optional AI decision suggestion. It runs only when the user enables it and uses only verified evidence, the deterministic risk analysis, and the generated forecast.
- Decision styles: Balanced, Risk-conscious, and Growth-oriented.
- Research quality / decision-readiness heuristic showing verification rate, source quality, domain diversity, and evidence coverage.
- Risk and forecast charts in the web UI.
- PDF report download with research-quality, risk, and forecast graphics.
- Markdown report download retained for portability and auditability.
- Improved research workflow labels and responsive mobile styling.

## Decision-support safeguards

The optional AI suggestion is advisory. Its confidence is evidence confidence rather than probability of business success. The report keeps the underlying sources, risks, assumptions, forecast warnings, decision questions, and limitations visible.

## Mobile access on the same Wi-Fi

The Windows frontend launcher binds Streamlit to `0.0.0.0:8501`. On the Windows PC, run `ipconfig`, find the Wi-Fi/Ethernet IPv4 address, then open `http://<PC-IP>:8501` on the Android device connected to the same local network. Windows Firewall may ask for permission for Python/Streamlit; allow access on private networks only.
