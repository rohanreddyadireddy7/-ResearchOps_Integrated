from app.analytics.forecast import ForecastService


def test_scenario_respects_forecast_horizon():
    f = ForecastService().build(
        [{'claim': 'Market CAGR is 12% through 2030', 'source_ids': ['S1']}],
        [], 100, years=2
    )
    assert f['method'] == 'evidence-based-scenario'
    assert len(f['scenarios']['base']['series']) == 3  # baseline + two forecast years


def test_ml_respects_forecast_horizon():
    hist = [
        {'year': 2021, 'value': 100}, {'year': 2022, 'value': 110},
        {'year': 2023, 'value': 121}, {'year': 2024, 'value': 133.1}
    ]
    f = ForecastService().build([], hist, None, years=3)
    assert f['method'] == 'ridge-log-trend-ml'
    assert len(f['forecast']) == 3
