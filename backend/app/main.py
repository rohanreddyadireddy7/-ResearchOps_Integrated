from concurrent.futures import ThreadPoolExecutor
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, Response
from app.core.config import get_settings
from app.models.schemas import ResearchRequest, ResearchAccepted, JobStatus
from app.storage.repository import Repository
from app.orchestrator import ResearchOrchestrator
from app.mapreduce.factory import get_mapreduce_engine
from app.reporting.pdf_report import build_pdf_report

s = get_settings()
repo = Repository()
executor = ThreadPoolExecutor(max_workers=max(2, s.research_workers))
app = FastAPI(title=s.app_name, version='1.2.0-gemini-ui')
app.add_middleware(
    CORSMiddleware,
    allow_origins=s.cors_origins if s.cors_origins != ['*'] else ['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.get('/health')
def health():
    missing = s.validate_runtime()
    try:
        engine = get_mapreduce_engine().name
    except Exception as e:
        engine = f'unavailable: {e}'
    return {
        'status': 'ok' if not missing else 'configuration_required',
        'missing': missing,
        'llm_provider': 'gemini',
        'mapreduce_engine': engine,
        'model': s.gemini_model,
        'version': app.version,
    }


@app.post('/research', response_model=ResearchAccepted, status_code=202)
def start_research(req: ResearchRequest):
    missing = s.validate_runtime()
    if missing:
        raise HTTPException(503, f'Missing configuration: {", ".join(missing)}')
    rid = str(uuid.uuid4())
    data = req.model_dump()
    repo.create(rid, req.question, data)
    executor.submit(ResearchOrchestrator(repo).run, rid, data)
    return {'research_id': rid, 'status': 'queued'}


@app.get('/research/{research_id}', response_model=JobStatus)
def get_research(research_id: str):
    j = repo.get(research_id)
    if not j:
        raise HTTPException(404, 'Research job not found')
    return {
        'research_id': research_id,
        'status': j['status'],
        'stage': j['stage'],
        'progress': j['progress'],
        'error': j['error'],
        'result': j['result']
    }


@app.get('/research/{research_id}/report', response_class=PlainTextResponse)
def report(research_id: str):
    j = repo.get(research_id)
    if not j or not j['result']:
        raise HTTPException(404, 'Completed report not found')
    return j['result']['report_markdown']


@app.get('/research/{research_id}/report.pdf')
def report_pdf(research_id: str):
    j = repo.get(research_id)
    if not j or not j['result']:
        raise HTTPException(404, 'Completed report not found')
    try:
        payload = build_pdf_report(j['result'])
    except Exception as e:
        raise HTTPException(500, f'Could not generate PDF report: {type(e).__name__}: {e}')
    return Response(
        content=payload,
        media_type='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="ResearchOps_{research_id[:8]}.pdf"'}
    )
