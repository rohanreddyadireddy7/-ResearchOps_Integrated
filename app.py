import os
import time
import pandas as pd
import requests
import streamlit as st

API = os.getenv('RESEARCHOPS_API', 'http://127.0.0.1:8000')

st.set_page_config(
    page_title='ResearchOps',
    page_icon='R',
    layout='wide',
    initial_sidebar_state='expanded',
)

st.markdown(
    """
<style>
:root {
    --ink: #111827;
    --muted: #4b5563;
    --line: #d9e1ea;
    --panel: #ffffff;
    --soft: #f6f8fb;
    --soft-blue: #eaf2fb;
    --soft-green: #edf7f1;
    --soft-amber: #fff7e8;
}

html, body, .stApp, .stApp * {
    color: var(--ink) !important;
}

.stApp {
    background: #f4f6f9;
}

.block-container {
    max-width: 1280px;
    padding-top: 1.4rem;
    padding-bottom: 3rem;
}

section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid var(--line);
}

section[data-testid="stSidebar"] * {
    color: var(--ink) !important;
}

.hero {
    background: linear-gradient(135deg, #ffffff 0%, #eef4fb 100%);
    border: 1px solid #ccd8e6;
    border-radius: 20px;
    padding: 30px 32px;
    margin-bottom: 22px;
    box-shadow: 0 10px 30px rgba(17, 24, 39, 0.05);
}

.hero h1 {
    font-size: clamp(2rem, 4vw, 3.1rem);
    margin: 0 0 8px 0;
    letter-spacing: -0.03em;
}

.hero p {
    max-width: 900px;
    margin: 0;
    line-height: 1.6;
    color: #263445 !important;
}

.eyebrow {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.panel, .card, .metric-card, .decision-card {
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: 15px;
    padding: 18px;
    box-shadow: 0 5px 18px rgba(17, 24, 39, 0.035);
}

.card {
    margin: 9px 0;
}

.card.finding { border-left: 4px solid #6b8eaa; }
.card.opportunity { border-left: 4px solid #719b7b; }
.card.risk { border-left: 4px solid #b48a50; }

.metric-card {
    text-align: center;
    min-height: 104px;
}

.metric-value {
    font-size: 1.75rem;
    line-height: 1.1;
    font-weight: 800;
    margin-bottom: 6px;
}

.metric-label {
    color: #526171 !important;
    font-size: 0.84rem;
}

.decision-card {
    background: #f3f7fb;
    border-color: #c8d7e7;
}

.decision-title {
    font-size: 1.15rem;
    font-weight: 800;
    margin-bottom: 4px;
}

.source-line {
    font-size: 0.80rem;
    color: #46576a !important;
    margin-top: 6px;
}

a, a:visited {
    color: #111827 !important;
    text-decoration: underline !important;
}

.stButton > button,
.stDownloadButton > button {
    background: #e7eef7 !important;
    color: #111827 !important;
    border: 1px solid #b9c8d8 !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #dbe7f4 !important;
    border-color: #8ca6bf !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #111827 !important;
}

[data-testid="stAlert"] {
    background: #f8fafc !important;
    border-color: #d7e0ea !important;
}

[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],
[data-testid="stMetricDelta"] {
    color: #111827 !important;
}

[data-testid="stDataFrame"] * {
    color: #111827 !important;
}

/* Keep dark code / research-query blocks readable. */
[data-testid="stCodeBlock"],
[data-testid="stCodeBlock"] pre,
[data-testid="stCodeBlock"] code,
[data-testid="stCodeBlock"] * {
    color: #ffffff !important;
}

[data-testid="stCodeBlock"],
[data-testid="stCodeBlock"] pre {
    background: #171a21 !important;
}

/* Force form controls and dropdown menus into a light, high-contrast treatment. */
div[data-baseweb="select"] > div,
div[data-baseweb="select"] input,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    background: #ffffff !important;
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
}

div[data-baseweb="select"] svg {
    fill: #111827 !important;
    color: #111827 !important;
}

[data-baseweb="popover"],
[data-baseweb="popover"] > div,
ul[role="listbox"],
li[role="option"] {
    background: #ffffff !important;
    color: #111827 !important;
}

[data-baseweb="popover"] *,
li[role="option"] * {
    color: #111827 !important;
}

li[role="option"]:hover {
    background: #eef3f8 !important;
}

textarea:disabled,
input:disabled {
    opacity: 1 !important;
    background: #ffffff !important;
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
}

input::placeholder,
textarea::placeholder {
    color: #6b7280 !important;
    opacity: 1 !important;
}

/* Keep Streamlit's top chrome light to avoid accidental dark-on-dark states. */
[data-testid="stHeader"] {
    background: rgba(255, 255, 255, 0.97) !important;
}

.small-note {
    color: #526171 !important;
    font-size: 0.82rem;
    line-height: 1.45;
}

.section-intro {
    color: #46576a !important;
    margin-top: -6px;
    margin-bottom: 16px;
}

@media (max-width: 768px) {
    .block-container {
        padding: 0.8rem 0.75rem 2rem 0.75rem;
    }
    .hero {
        padding: 22px 18px;
        border-radius: 14px;
    }
    .panel, .card, .metric-card, .decision-card {
        padding: 14px;
        border-radius: 12px;
    }
    div[data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        gap: 0.65rem !important;
    }
    div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
    .metric-card {
        min-height: auto;
        text-align: left;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


def api_get(path, timeout=20):
    return requests.get(API + path, timeout=timeout)


def source_links(ids, catalog):
    by = {s['source_id']: s for s in catalog}
    links = []
    for sid in ids:
        if sid in by:
            links.append(f"[{sid}: {by[sid].get('domain','source')}]({by[sid].get('url','')})")
    return ' · '.join(links)


def render_item(item, catalog, kind='finding'):
    text = item.get('text') or item.get('claim', '')
    st.markdown(f"<div class='card {kind}'><b>{text}</b></div>", unsafe_allow_html=True)
    if item.get('rationale'):
        st.caption(item['rationale'])
    if item.get('mitigation'):
        st.caption('Mitigation: ' + item['mitigation'])
    links = source_links(item.get('source_ids', []), catalog)
    if links:
        st.markdown('**Sources:** ' + links)


def metric_card(value, label):
    st.markdown(
        f"<div class='metric-card'><div class='metric-value'>{value}</div><div class='metric-label'>{label}</div></div>",
        unsafe_allow_html=True,
    )


def render_forecast(fc):
    note = fc.get('warning') or fc.get('message', '')
    if note:
        st.caption(note)
    if fc.get('method') == 'evidence-based-scenario':
        rows = []
        for name, obj in fc.get('scenarios', {}).items():
            for p in obj.get('series', []):
                rows.append({'Scenario': name.title(), 'Year': p['year'], 'Projected value': p['value']})
        if rows:
            df = pd.DataFrame(rows)
            st.line_chart(df, x='Year', y='Projected value', color='Scenario', use_container_width=True)
            summary = []
            for name, obj in fc.get('scenarios', {}).items():
                series = obj.get('series', [])
                summary.append({
                    'Scenario': name.title(),
                    'Annual rate': f"{obj.get('annual_rate',0)*100:.2f}%",
                    'Final projected value': series[-1]['value'] if series else None,
                })
            st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)
    elif fc.get('method') == 'ridge-log-trend-ml':
        rows = fc.get('forecast', [])
        if rows:
            df = pd.DataFrame(rows)
            st.line_chart(df.set_index('year')[['predicted', 'p10', 'p90']], use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info('The research did not contain enough defensible growth data for a numeric forecast. Add historical values or broaden the research scope.')


def _confidence_label(confidence):
    if confidence >= 85:
        return 'Very high'
    if confidence >= 70:
        return 'High'
    if confidence >= 50:
        return 'Moderate'
    if confidence >= 30:
        return 'Low'
    return 'Very low'


def render_decision(advice, catalog):
    if not advice or not advice.get('enabled'):
        return

    confidence = int(advice.get('confidence', 0) or 0)
    confidence = max(0, min(100, confidence))
    stance = advice.get('stance', 'Insufficient evidence')
    summary = advice.get('summary', '')

    st.markdown('### AI Decision Suggestion')
    st.caption('This is an optional evidence-grounded suggestion. The final decision remains with the user.')

    decision_col, confidence_col = st.columns([3, 1])
    with decision_col:
        st.text_area(
            'Decision',
            value=f"{stance}\n\n{summary}".strip(),
            height=150,
            disabled=True,
            help='The recommendation is generated from verified findings, calculated risks and the selected forecast. It does not add unsupported facts.',
        )
    with confidence_col:
        st.metric('AI confidence', f'{confidence}%')
        st.progress(confidence / 100.0)
        st.caption(f"Certainty level: {_confidence_label(confidence)}")

    st.caption('Confidence reflects the strength and consistency of the available evidence; it is not a guarantee that the outcome will occur.')

    if advice.get('reasons'):
        st.markdown('**Evidence behind the suggestion**')
        for x in advice['reasons']:
            st.markdown(f"- {x.get('text','')}")
            links = source_links(x.get('source_ids', []), catalog)
            if links:
                st.markdown('  Sources: ' + links)
    if advice.get('conditions'):
        st.markdown('**Conditions before acting**')
        for x in advice['conditions']:
            st.markdown(f"- {x}")
    if advice.get('next_actions'):
        st.markdown('**Recommended next actions**')
        for x in advice['next_actions']:
            st.markdown(f"- {x}")
    if advice.get('watchouts'):
        st.markdown('**Watchouts**')
        for x in advice['watchouts']:
            st.markdown(f"- {x}")
    st.caption(advice.get('note', ''))


if 'research_id' not in st.session_state:
    st.session_state.research_id = None
if 'result' not in st.session_state:
    st.session_state.result = None

with st.sidebar:
    st.markdown('## ResearchOps')
    st.caption('Evidence-backed research and decision support')
    page = st.radio('Navigation', ['Research Workspace', 'Research Trail', 'Final Report'])
    st.markdown('---')
    try:
        h = api_get('/health').json()
        st.markdown('**System status**')
        st.caption(f"Backend: {h.get('status')}")
        st.caption(f"AI: {h.get('llm_provider','unknown')} / {h.get('model','unknown')}")
        st.caption(f"Processing: {h.get('mapreduce_engine','unknown')}")
        if h.get('missing'):
            st.warning('Missing configuration: ' + ', '.join(h['missing']))
    except Exception:
        st.warning('Backend is not reachable.')
    st.markdown('---')
    if st.button('Start New Research', use_container_width=True):
        st.session_state.research_id = None
        st.session_state.result = None
        st.rerun()

st.markdown(
    """
<div class='hero'>
  <div class='eyebrow'>Research intelligence workspace</div>
  <h1>ResearchOps</h1>
  <p>Turn a complex problem into parallel research tasks, verified evidence, opportunity and risk analysis, a configurable 1–5 year forecast, and an optional AI decision suggestion with source-backed reasoning.</p>
</div>
""",
    unsafe_allow_html=True,
)

if page == 'Research Workspace':
    st.subheader('1. Define the research problem')
    st.markdown("<div class='section-intro'>Describe the decision you are evaluating. The system will decompose it into independent research tasks and verify the evidence before using it.</div>", unsafe_allow_html=True)

    question = st.text_area(
        'Problem statement',
        height=125,
        placeholder='Example: Should we launch a premium EV subscription service for urban professionals in Bengaluru?'
    )

    c1, c2 = st.columns(2)
    geography = c1.text_input('Geography (optional)', placeholder='Bengaluru, India')
    industry = c2.text_input('Industry (optional)', placeholder='Electric mobility / subscription services')

    st.subheader('2. Configure analysis')
    f1, f2, f3 = st.columns(3)
    forecast_years = f1.select_slider('Forecast horizon', options=[1, 2, 3, 4, 5], value=5, format_func=lambda x: f'{x} year' if x == 1 else f'{x} years')
    max_tasks = f2.slider('Research tasks', 3, 10, 5)
    sources_per_task = f3.slider('Sources per task', 2, 8, 4)

    decision_support = st.toggle(
        'Include an AI decision suggestion',
        value=False,
        help='Adds one final Gemini analysis step that reviews only the verified evidence, forecast and risk results. It is advisory, not an automatic decision.'
    )
    decision_style = 'Balanced'
    if decision_support:
        decision_style = st.selectbox(
            'Decision style',
            ['Balanced', 'Risk-conscious', 'Growth-oriented'],
            help='Changes how the optional decision suggestion weighs uncertainty, downside risk and opportunity. It does not change the underlying evidence.'
        )

    with st.expander('What do these analysis options mean?'):
        st.markdown(
            '''
- **Forecast horizon:** choose how many future years (1–5) the projection should cover.
- **Research tasks:** controls how many smaller research questions the original problem is divided into. More tasks can broaden coverage but take longer.
- **Sources per task:** controls how many web sources are collected for each research task. More sources can improve evidence diversity but use more search quota.
- **AI decision suggestion:** asks Gemini to review only the verified findings, risk analysis and forecast and provide an advisory recommendation.
- **Decision style:** *Balanced* weighs opportunity and risk evenly; *Risk-conscious* emphasizes uncertainty/downside; *Growth-oriented* gives more weight to upside opportunities while still reporting risks.
- **Forecast data:** optional baseline and historical values. With enough historical observations, the system can use its trend model; otherwise it uses evidence-based scenarios when defensible growth data is available.
            '''
        )

    with st.expander('Forecast data (optional)'):
        baseline = st.number_input(
            'Current market/revenue baseline',
            min_value=0.0,
            value=0.0,
            help='Used as the starting value for evidence-based scenarios. Leave at 0 to use an index baseline of 100.'
        )
        st.caption('For a trained trend model, provide at least four historical year/value rows. Otherwise the system uses evidence-based scenarios only when explicit growth rates are found.')
        hist = st.data_editor(
            pd.DataFrame(columns=['year', 'value']),
            num_rows='dynamic',
            use_container_width=True,
            hide_index=True,
        )

    if st.button('Start Research', type='primary', use_container_width=True):
        if not question.strip():
            st.warning('Enter a problem statement before starting research.')
        else:
            history = []
            for _, row in hist.dropna().iterrows():
                try:
                    history.append({'year': int(row['year']), 'value': float(row['value'])})
                except Exception:
                    pass
            payload = {
                'question': question,
                'geography': geography or None,
                'industry': industry or None,
                'max_tasks': max_tasks,
                'sources_per_task': sources_per_task,
                'baseline_value': baseline or None,
                'historical_data': history,
                'forecast_years': forecast_years,
                'include_decision_suggestion': decision_support,
                'decision_style': decision_style,
            }
            try:
                response = requests.post(API + '/research', json=payload, timeout=30)
                if not response.ok:
                    try:
                        detail = response.json().get('detail') or response.text
                    except Exception:
                        detail = response.text
                    st.error(f'Could not start research: {detail}')
                else:
                    st.session_state.research_id = response.json()['research_id']
                    st.session_state.result = None
            except Exception as e:
                st.error(f'Could not reach backend: {e}')

    if st.session_state.research_id and not st.session_state.result:
        status_box = st.empty()
        progress = st.progress(0)
        for _ in range(180):
            try:
                job_response = api_get('/research/' + st.session_state.research_id)
                job = job_response.json()
                progress.progress(int(job['progress']))
                status_box.info(f"{job['stage']} - {job['progress']}%")
                if job['status'] == 'completed':
                    st.session_state.result = job['result']
                    status_box.success('Research completed.')
                    break
                if job['status'] == 'failed':
                    status_box.error(job.get('error') or 'Research failed.')
                    break
            except Exception as e:
                status_box.error(str(e))
                break
            time.sleep(2)
        if st.session_state.result:
            st.rerun()

    if st.session_state.result:
        r = st.session_state.result
        m = r['metrics']
        quality = r.get('research_quality', {})
        catalog = r['source_catalog']

        st.markdown('---')
        st.subheader('Research summary')
        a, b, c, d, e = st.columns(5)
        with a: metric_card(m.get('tasks', 0), 'Research tasks')
        with b: metric_card(m.get('sources_retrieved', 0), 'Sources reviewed')
        with c: metric_card(m.get('verified_findings', 0), 'Verified findings')
        with d: metric_card(quality.get('unique_domains', 0), 'Independent domains')
        with e: metric_card(f"{quality.get('readiness_score',0)}/100", 'Decision readiness')

        st.caption(quality.get('note', ''))
        st.info(r['verification_note'])

        render_decision(r.get('decision_suggestion'), catalog)

        st.subheader('Executive summary')
        st.markdown(r.get('synthesis', {}).get('executive_summary', ''))
        exec_links = source_links(r.get('synthesis', {}).get('executive_source_ids', []), catalog)
        if exec_links:
            st.markdown('**Sources:** ' + exec_links)

        tab1, tab2, tab3, tab4 = st.tabs(['Evidence', 'Opportunities', 'Risk', 'Forecast'])
        with tab1:
            for finding in r.get('verified_findings', []):
                render_item(finding, catalog, 'finding')
        with tab2:
            opportunities = r.get('synthesis', {}).get('opportunities', [])
            if not opportunities:
                st.info('No evidence-backed opportunities were identified.')
            for item in opportunities:
                render_item(item, catalog, 'opportunity')
        with tab3:
            ra = r.get('risk_assessment', {})
            x1, x2 = st.columns(2)
            x1.metric('Aggregate risk score', f"{ra.get('overall_score',0)}/100")
            x2.metric('Risk band', ra.get('band', 'Unknown'))
            risks = ra.get('risks', [])
            if risks:
                risk_df = pd.DataFrame([
                    {'Risk': x.get('text',''), 'Likelihood': x.get('likelihood',0), 'Impact': x.get('impact',0), 'Score': x.get('score',0)}
                    for x in risks
                ])
                st.bar_chart(risk_df.set_index('Risk')['Score'], use_container_width=True)
            for item in risks:
                render_item(item, catalog, 'risk')
                st.caption(f"Likelihood {item['likelihood']}/5 · Impact {item['impact']}/5 · Risk score {item['score']}/25")
            if ra.get('monte_carlo'):
                mc = ra['monte_carlo']
                st.caption(f"Monte Carlo mean impact index: {mc['mean_impact_index']} · P90 impact index: {mc['p90_impact_index']} · {mc['simulation_runs']} runs")
        with tab4:
            st.markdown(f"**Selected horizon:** {r.get('request_options',{}).get('forecast_years',5)} year(s)")
            render_forecast(r.get('forecast', {}))
            ev_ids = sorted({sid for evi in r.get('forecast', {}).get('evidence', []) for sid in evi.get('source_ids', [])})
            if ev_ids:
                st.markdown('**Forecast evidence:** ' + source_links(ev_ids, catalog))

        st.subheader('Source register')
        if catalog:
            source_df = pd.DataFrame(catalog)
            cols = [x for x in ['source_id', 'title', 'domain', 'quality_score', 'url'] if x in source_df.columns]
            st.dataframe(source_df[cols], use_container_width=True, hide_index=True)

elif page == 'Research Trail':
    if not st.session_state.result:
        st.info('Run research first. The complete research trail will appear here.')
    else:
        r = st.session_state.result
        st.subheader('Research trail')
        st.markdown("<div class='section-intro'>This view shows how the original question was decomposed and how the research data was processed.</div>", unsafe_allow_html=True)
        for i, task in enumerate(r.get('plan', {}).get('tasks', []), 1):
            st.markdown(f"**{i}. {task.get('topic','')}**")
            st.write(task.get('purpose', ''))
            st.code(task.get('research_query', ''), language=None)
        st.markdown('---')
        st.markdown(f"**MapReduce engine:** {r.get('mapreduce',{}).get('engine','')}")
        st.json(r.get('mapreduce', {}).get('summary', {}), expanded=False)

elif page == 'Final Report':
    if not st.session_state.result:
        st.info('Run research first. Your downloadable report will appear here.')
    else:
        r = st.session_state.result
        catalog = r.get('source_catalog', [])
        st.subheader('Final decision report')
        st.markdown("<div class='section-intro'>The PDF version includes graphical summaries for research quality, priority risks and the selected forecast horizon.</div>", unsafe_allow_html=True)

        render_decision(r.get('decision_suggestion'), catalog)
        st.markdown(r.get('report_markdown', ''))

        st.markdown('---')
        d1, d2 = st.columns(2)
        with d1:
            st.download_button(
                'Download Markdown Report',
                data=r.get('report_markdown', ''),
                file_name='ResearchOps_Report.md',
                mime='text/markdown',
                use_container_width=True,
            )
        with d2:
            try:
                pdf_response = api_get(f"/research/{r['research_id']}/report.pdf", timeout=60)
                if pdf_response.ok:
                    st.download_button(
                        'Download PDF Report with Charts',
                        data=pdf_response.content,
                        file_name='ResearchOps_Report.pdf',
                        mime='application/pdf',
                        use_container_width=True,
                    )
                else:
                    st.warning('PDF report is not available yet. Markdown download is still available.')
            except Exception as e:
                st.warning(f'PDF report could not be prepared: {e}')
