import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.core.config import get_settings
from app.agents.planner import PlannerAgent
from app.agents.evidence import EvidenceAgent
from app.agents.synthesizer import SynthesisAgent
from app.agents.decision import DecisionAgent
from app.services.search_service import SearchService
from app.mapreduce.factory import get_mapreduce_engine
from app.analytics.forecast import ForecastService
from app.analytics.risk import RiskService
from app.storage.repository import Repository


class ResearchOrchestrator:
    def __init__(self, repo=None):
        self.s = get_settings()
        self.repo = repo or Repository()

    def _stage(self, rid, stage, progress):
        self.repo.update(rid, status='running', stage=stage, progress=progress)

    def _quality(self, claims, verified, sources):
        verification_rate = (len(verified) / len(claims) * 100) if claims else 0.0
        unique_domains = len({s.get('domain') for s in sources if s.get('domain')})
        avg_quality = sum(float(s.get('quality_score', 0)) for s in sources) / max(1, len(sources))
        domain_score = min(100.0, unique_domains / 8.0 * 100.0)
        evidence_coverage = min(100.0, len(verified) / 8.0 * 100.0)
        readiness = (
            0.30 * verification_rate
            + 0.25 * (avg_quality * 100.0)
            + 0.25 * domain_score
            + 0.20 * evidence_coverage
        )
        band = 'Limited' if readiness < 40 else 'Developing' if readiness < 65 else 'Strong'
        return {
            'readiness_score': round(readiness, 1),
            'band': band,
            'verification_rate': round(verification_rate, 1),
            'unique_domains': unique_domains,
            'average_source_quality': round(avg_quality, 3),
            'domain_diversity_score': round(domain_score, 1),
            'evidence_coverage_score': round(evidence_coverage, 1),
            'note': 'Decision readiness is a heuristic combining verification rate, source quality, domain diversity and evidence coverage. It is not a guarantee that a decision will succeed.'
        }

    def run(self, rid, req):
        try:
            self._stage(rid, 'Planning research tasks', 8)
            planner = PlannerAgent()
            plan = planner.create_plan(req['question'], req['max_tasks'], req.get('geography'), req.get('industry'))
            tasks = plan.get('tasks', [])

            self._stage(rid, 'Collecting sources in parallel', 18)
            search = SearchService()
            sources = []

            def fetch(task):
                query = task['research_query']
                if req.get('geography') and req['geography'].lower() not in query.lower():
                    query += f" {req['geography']}"
                rows = search.search(query, req['sources_per_task'])
                for r in rows:
                    r.update({'task_id': task['task_id'], 'topic': task['topic'], 'query': query})
                return rows

            with ThreadPoolExecutor(max_workers=self.s.research_workers) as ex:
                futs = {ex.submit(fetch, t): t for t in tasks}
                for f in as_completed(futs):
                    sources.extend(f.result())

            dedup = {}
            for s in sources:
                if s.get('url') and s['url'] not in dedup:
                    dedup[s['url']] = s
            sources = list(dedup.values())
            for i, s in enumerate(sources, 1):
                s['source_id'] = f'S{i}'

            self._stage(rid, 'MapReduce processing', 38)
            engine = get_mapreduce_engine()
            mr = engine.run(sources, rid)

            self._stage(rid, 'Extracting evidence claims', 52)
            ev = EvidenceAgent()
            claims = []
            for t in tasks:
                ts = [s for s in sources if s['task_id'] == t['task_id']]
                if ts:
                    claims.extend(ev.extract_claims(t, ts))

            self._stage(rid, 'Verifying claims against sources', 66)
            verified_raw = []
            for t in tasks:
                tc = [c for c in claims if c['task_id'] == t['task_id']]
                ts = [s for s in sources if s['task_id'] == t['task_id']]
                if tc and ts:
                    verified_raw.extend(ev.verify_claims(tc, ts))

            by_source = {s['source_id']: s for s in sources}
            verified = []
            for c in verified_raw:
                if c.get('verification_status') != 'supported' or not c.get('source_ids'):
                    continue
                domains = {by_source[x]['domain'] for x in c['source_ids'] if x in by_source}
                qualities = [by_source[x]['quality_score'] for x in c['source_ids'] if x in by_source]
                corroborated = len(domains) >= 2
                primary = bool(qualities and max(qualities) >= 0.9)
                if not (corroborated or primary):
                    continue
                confidence = min(0.98, 0.55 + 0.12 * len(domains) + (0.18 if primary else 0) + 0.08 * (sum(qualities) / max(1, len(qualities))))
                c['confidence'] = round(confidence, 3)
                c['evidence_strength'] = 'corroborated' if corroborated else 'authoritative-primary'
                c['finding_id'] = f'F{len(verified) + 1}'
                verified.append(c)

            self._stage(rid, 'Synthesizing research findings', 77)
            synth = SynthesisAgent()
            synthesis = synth.synthesize(req['question'], verified, sources) if verified else {
                'executive_summary': 'No claims met the strict verification threshold.',
                'executive_source_ids': [],
                'key_findings': [], 'opportunities': [], 'risks': [], 'decision_questions': [],
                'limitations': ['No claim was corroborated by two independent domains or one high-authority primary source.']
            }

            self._stage(rid, 'Forecasting and risk analysis', 88)
            forecast = ForecastService().build(
                verified,
                [dict(x) for x in req.get('historical_data', [])],
                req.get('baseline_value'),
                years=int(req.get('forecast_years', 5)),
            )
            risk = RiskService().assess(synthesis.get('risks', []))
            quality = self._quality(claims, verified, sources)

            decision = {'enabled': False}
            if req.get('include_decision_suggestion'):
                self._stage(rid, 'Preparing optional AI decision suggestion', 95)
                if verified:
                    decision = DecisionAgent().advise(
                        req['question'], synthesis, risk, forecast, verified, sources,
                        style=req.get('decision_style', 'Balanced')
                    )
                else:
                    decision = {
                        'enabled': True,
                        'stance': 'Insufficient evidence',
                        'confidence': 0,
                        'summary': 'The strict verification stage did not retain enough evidence to support a responsible recommendation.',
                        'reasons': [], 'conditions': [],
                        'next_actions': ['Broaden the research scope, add primary sources, or provide trusted internal data before making the decision.'],
                        'watchouts': [],
                        'style': req.get('decision_style', 'Balanced'),
                        'note': 'AI decision support is advisory and should not replace human review.'
                    }

            report = self._markdown(req['question'], synthesis, verified, sources, forecast, risk, engine.name, decision, quality, int(req.get('forecast_years', 5)))
            result = {
                'research_id': rid,
                'question': req['question'],
                'request_options': {
                    'forecast_years': int(req.get('forecast_years', 5)),
                    'include_decision_suggestion': bool(req.get('include_decision_suggestion')),
                    'decision_style': req.get('decision_style', 'Balanced'),
                },
                'plan': plan,
                'metrics': {
                    'tasks': len(tasks), 'sources_retrieved': len(sources), 'claims_extracted': len(claims),
                    'verified_findings': len(verified), 'rejected_or_uncertain': max(0, len(claims) - len(verified))
                },
                'research_quality': quality,
                'mapreduce': {'engine': engine.name, 'summary': mr},
                'verified_findings': verified,
                'source_catalog': [
                    {k: s[k] for k in ('source_id','title','url','domain','quality_score','search_score','retrieved_at','task_id','topic') if k in s}
                    for s in sources
                ],
                'synthesis': synthesis,
                'forecast': forecast,
                'risk_assessment': risk,
                'decision_suggestion': decision,
                'report_markdown': report,
                'verification_note': 'Verified means the retrieved excerpts directly supported the claim and it was corroborated across at least two domains or backed by a high-authority primary source. It does not mean absolute truth.'
            }
            self.repo.update(rid, status='completed', stage='Completed', progress=100, result_json=json.dumps(result))
        except Exception as e:
            self.repo.update(rid, status='failed', stage='Failed', progress=100, error=f'{type(e).__name__}: {e}')

    def _cite(self, ids, sources):
        by = {s['source_id']: s for s in sources}
        return ' '.join(f"[{i}]({by[i]['url']})" for i in ids if i in by)

    def _markdown(self, q, syn, findings, sources, forecast, risk, engine, decision, quality, forecast_years):
        lines = [
            '# ResearchOps Report', '', f'**Problem statement:** {q}', '',
            f'**Processing mode:** {engine}', f'**Forecast horizon:** {forecast_years} year(s)', '',
            '## Research Quality', '',
            f"**Decision readiness:** {quality.get('readiness_score',0)}/100 - {quality.get('band','Unknown')}",
            f"Verification rate: {quality.get('verification_rate',0)}% | Unique domains: {quality.get('unique_domains',0)} | Average source quality: {quality.get('average_source_quality',0)*100:.0f}%",
            '', quality.get('note',''), '',
            '## Executive Summary', '', syn.get('executive_summary',''),
            f"  \nSources: {self._cite(syn.get('executive_source_ids',[]),sources)}" if syn.get('executive_source_ids') else ''
        ]
        if decision.get('enabled'):
            lines += ['', '## AI Decision Suggestion', '', f"**{decision.get('stance','')}** - Confidence {decision.get('confidence',0)}%", '', decision.get('summary','')]
            for x in decision.get('reasons', []):
                lines += [f"- {x.get('text','')}  ", f"  Sources: {self._cite(x.get('source_ids',[]),sources)}"]
            if decision.get('conditions'):
                lines += ['', '### Conditions before acting'] + [f'- {x}' for x in decision['conditions']]
            if decision.get('next_actions'):
                lines += ['', '### Recommended next actions'] + [f'- {x}' for x in decision['next_actions']]
            if decision.get('watchouts'):
                lines += ['', '### Watchouts'] + [f'- {x}' for x in decision['watchouts']]
            lines += ['', f"_{decision.get('note','')}_"]

        lines += ['', '## Verified Findings', '']
        for f in findings:
            lines += [f"- {f['claim']}  ", f"  Sources: {self._cite(f['source_ids'],sources)}"]
        lines += ['', '## Business Opportunities', '']
        for x in syn.get('opportunities', []):
            lines += [f"- **{x.get('text','')}** - {x.get('rationale','')}  ", f"  Sources: {self._cite(x.get('source_ids',[]),sources)}"]
        lines += ['', '## Risks', '']
        for x in risk.get('risks', []):
            lines += [
                f"- **{x.get('text','')}** (Likelihood {x['likelihood']}/5, Impact {x['impact']}/5, Score {x['score']}/25)  ",
                f"  Mitigation: {x.get('mitigation','')}  ",
                f"  Sources: {self._cite(x.get('source_ids',[]),sources)}"
            ]
        lines += ['', '### Aggregate risk score', f"**{risk.get('overall_score',0)}/100 - {risk.get('band','Unknown')}**", '', '## Forecast', '', f"Method: **{forecast.get('method')}**", '', forecast.get('warning') or forecast.get('message','')]
        if forecast.get('method') == 'evidence-based-scenario':
            lines += ['', '| Scenario | Annual rate | Final projected value |', '|---|---:|---:|']
            for name, obj in forecast.get('scenarios', {}).items():
                series = obj.get('series', [])
                final = series[-1]['value'] if series else 0
                lines.append(f"| {name.title()} | {obj.get('annual_rate',0)*100:.2f}% | {final:.2f} |")
        elif forecast.get('method') == 'ridge-log-trend-ml':
            lines += ['', '| Year | Predicted | P10 | P90 |', '|---:|---:|---:|---:|']
            for row in forecast.get('forecast', []):
                lines.append(f"| {row['year']} | {row['predicted']:.2f} | {row['p10']:.2f} | {row['p90']:.2f} |")
        if forecast.get('evidence'):
            all_ids = sorted({sid for e in forecast['evidence'] for sid in e.get('source_ids', [])})
            lines += [f"  Sources: {self._cite(all_ids,sources)}"]
        lines += ['', '## Decision Questions', '']
        for x in syn.get('decision_questions', []):
            lines.append(f'- {x}')
        lines += ['', '## Limitations', '']
        for x in syn.get('limitations', []):
            lines.append(f'- {x}')
        lines += ['', '## Source Register', '']
        for s in sources:
            lines.append(f"- **{s['source_id']}** - [{s['title']}]({s['url']}) - {s['domain']}")
        return '\n'.join(lines)
