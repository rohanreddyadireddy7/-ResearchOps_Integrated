import math, re
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score

RATE_RE=re.compile(r'(?<!\d)(-?\d+(?:\.\d+)?)\s*%')
CONTEXT=('cagr','growth','grew','increase','increased','decline','declined','annual','year-on-year','yoy')

class ForecastService:
    def build(self, findings, historical_data=None, baseline_value=None, years=5):
        history=sorted(historical_data or [], key=lambda x:x['year'])
        if len(history)>=4:
            return self._ml_forecast(history, years)
        rates=[]
        for f in findings:
            low=f['claim'].lower()
            if not any(k in low for k in CONTEXT): continue
            for m in RATE_RE.finditer(f['claim']):
                v=float(m.group(1))/100.0
                if -0.8 <= v <= 2.0: rates.append((v,f['source_ids'],f['claim']))
        if not rates:
            return {'method':'insufficient-evidence','available':False,'message':'No defensible growth-rate evidence or historical series was found. Add at least four year/value observations for an ML forecast, or research sources containing explicit growth rates.'}
        vals=np.array([x[0] for x in rates],dtype=float)
        base=float(np.median(vals)); downside=float(np.quantile(vals,0.25)); upside=float(np.quantile(vals,0.75))
        if len(vals)==1:
            spread=max(abs(base)*0.35,0.03); downside=base-spread; upside=base+spread
        downside=max(downside,-0.8); upside=min(upside,2.0)
        start=float(baseline_value or 100.0); indexed=baseline_value is None
        scenarios={}
        for name,rate in [('downside',downside),('base',base),('upside',upside)]:
            series=[]
            for y in range(0,years+1): series.append({'year':y,'value':round(start*((1+rate)**y),3)})
            scenarios[name]={'annual_rate':round(rate,4),'series':series}
        return {'method':'evidence-based-scenario','available':True,'indexed_baseline':indexed,'baseline':start,'scenarios':scenarios,'evidence':[{'rate':r,'source_ids':s,'claim':c} for r,s,c in rates[:8]],'warning':'Scenario projection, not a trained predictive model. Rates are taken only from retrieved evidence.'}

    def _ml_forecast(self, history, years):
        ys=np.array([p['year'] for p in history],dtype=float); vals=np.array([p['value'] for p in history],dtype=float)
        y0=ys.min(); X=(ys-y0).reshape(-1,1); logy=np.log(vals)
        model=Ridge(alpha=0.5).fit(X,logy); fitted=np.exp(model.predict(X)); r2=float(r2_score(vals,fitted))
        future_years=np.arange(int(ys.max())+1,int(ys.max())+years+1); Xf=(future_years-y0).reshape(-1,1); pred=np.exp(model.predict(Xf))
        residual=np.std(logy-model.predict(X)) if len(vals)>2 else 0.12
        rng=np.random.default_rng(42); sims=[]
        for _ in range(1500): sims.append(np.exp(model.predict(Xf)+rng.normal(0,max(residual,0.03),size=len(Xf))))
        sims=np.array(sims)
        rows=[]
        for i,year in enumerate(future_years): rows.append({'year':int(year),'predicted':round(float(pred[i]),3),'p10':round(float(np.quantile(sims[:,i],0.10)),3),'p90':round(float(np.quantile(sims[:,i],0.90)),3)})
        cagr=float((pred[-1]/vals[-1])**(1/years)-1)
        return {'method':'ridge-log-trend-ml','available':True,'training_points':len(history),'in_sample_r2':round(r2,4),'implied_annual_growth':round(cagr,4),'forecast':rows,'warning':'Statistical extrapolation from user-supplied historical data; it is not a guarantee and can fail under structural market changes.'}
