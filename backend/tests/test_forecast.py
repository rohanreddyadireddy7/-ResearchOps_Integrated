from app.analytics.forecast import ForecastService

def test_scenario():
    f=ForecastService().build([{'claim':'Market CAGR is 12% through 2030','source_ids':['S1']}],[],100)
    assert f['available'] is True
    assert f['method']=='evidence-based-scenario'

def test_ml():
    hist=[{'year':2021,'value':100},{'year':2022,'value':110},{'year':2023,'value':121},{'year':2024,'value':133.1}]
    f=ForecastService().build([],hist,None)
    assert f['method']=='ridge-log-trend-ml'
    assert len(f['forecast'])==5
