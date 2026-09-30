import json
from app.services.gemini_service import GeminiService


class DecisionAgent:
    """Optional evidence-grounded decision aid. It never invents evidence."""

    def __init__(self, llm=None):
        self.llm = llm or GeminiService()

    def advise(self, question, synthesis, risk, forecast, verified_findings, source_catalog, style='Balanced'):
        valid_sources = {s['source_id'] for s in source_catalog}
        evidence = [
            {
                'finding_id': f.get('finding_id'),
                'claim': f.get('claim'),
                'source_ids': f.get('source_ids', []),
                'confidence': f.get('confidence'),
            }
            for f in verified_findings
        ]
        compact_forecast = {
            'method': forecast.get('method'),
            'available': forecast.get('available'),
            'scenarios': forecast.get('scenarios'),
            'forecast': forecast.get('forecast'),
            'warning': forecast.get('warning') or forecast.get('message'),
        }
        compact_risk = {
            'overall_score': risk.get('overall_score'),
            'band': risk.get('band'),
            'risks': risk.get('risks', []),
        }
        instructions = """You are an evidence-grounded business decision-support agent. Use ONLY the supplied verified evidence, synthesis, deterministic risk analysis and forecast. Do not add outside facts. This is an optional suggestion for a human decision-maker, not an instruction or guarantee. Return ONLY JSON with this structure: {"stance":"Proceed|Proceed with conditions|Delay|Do not proceed|Insufficient evidence","confidence":0-100,"summary":str,"reasons":[{"text":str,"source_ids":[str]}],"conditions":[str],"next_actions":[str],"watchouts":[str]}. Confidence must reflect evidence strength, not rhetorical certainty. If evidence is weak, choose Insufficient evidence or Delay. Keep the summary under 140 words and include 2-5 reasons when evidence permits."""
        prompt = (
            f"Decision question: {question}\n"
            f"Decision style: {style}\n"
            f"Verified evidence: {json.dumps(evidence)}\n"
            f"Synthesis: {json.dumps(synthesis)}\n"
            f"Risk analysis: {json.dumps(compact_risk)}\n"
            f"Forecast: {json.dumps(compact_forecast)}"
        )
        data = self.llm.json(instructions, prompt)
        stance = data.get('stance', 'Insufficient evidence')
        allowed = {'Proceed', 'Proceed with conditions', 'Delay', 'Do not proceed', 'Insufficient evidence'}
        if stance not in allowed:
            stance = 'Insufficient evidence'
        try:
            confidence = max(0, min(100, int(data.get('confidence', 0))))
        except Exception:
            confidence = 0
        reasons = []
        for item in data.get('reasons', []) or []:
            if not isinstance(item, dict) or not item.get('text'):
                continue
            ids = [x for x in item.get('source_ids', []) if x in valid_sources]
            reasons.append({'text': item['text'], 'source_ids': ids})
        return {
            'enabled': True,
            'stance': stance,
            'confidence': confidence,
            'summary': data.get('summary', ''),
            'reasons': reasons[:5],
            'conditions': [str(x) for x in (data.get('conditions') or [])][:6],
            'next_actions': [str(x) for x in (data.get('next_actions') or [])][:6],
            'watchouts': [str(x) for x in (data.get('watchouts') or [])][:6],
            'style': style,
            'note': 'AI decision support is advisory. Review the cited evidence, assumptions, risks and forecast before acting.'
        }
