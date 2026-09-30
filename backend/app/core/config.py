from functools import lru_cache
from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
for candidate in (BASE_DIR / '.env', BASE_DIR / 'api.env', BASE_DIR.parent / 'api.env'):
    if candidate.exists():
        load_dotenv(candidate, override=False)


class Settings:
    app_name = os.getenv('APP_NAME', 'ResearchOps API')
    api_host = os.getenv('API_HOST', '127.0.0.1')
    api_port = int(os.getenv('API_PORT', '8000'))

    # LLM provider: Gemini Developer API (Google AI Studio key)
    gemini_api_key = os.getenv('GEMINI_API_KEY', '')
    gemini_model = os.getenv('GEMINI_MODEL', 'gemini-3.5-flash-lite')
    gemini_fallback_models = [
        x.strip() for x in os.getenv('GEMINI_FALLBACK_MODELS', 'gemini-3.5-flash').split(',') if x.strip()
    ]
    gemini_max_retries = int(os.getenv('GEMINI_MAX_RETRIES', '1'))

    tavily_api_key = os.getenv('TAVILY_API_KEY', '')
    research_workers = int(os.getenv('RESEARCH_WORKERS', '6'))
    hadoop_mode = os.getenv('HADOOP_MODE', 'local').lower()  # auto | local | streaming
    hadoop_binary = os.getenv('HADOOP_BINARY', 'hadoop')
    hadoop_streaming_jar = os.getenv('HADOOP_STREAMING_JAR', '')
    data_dir = Path(os.getenv('DATA_DIR', str(BASE_DIR / 'data')))
    db_path = data_dir / 'researchops.db'
    max_source_chars = int(os.getenv('MAX_SOURCE_CHARS', '5000'))
    cors_origins = [x.strip() for x in os.getenv('CORS_ORIGINS', '*').split(',') if x.strip()]

    def validate_runtime(self):
        missing = []
        if not self.gemini_api_key:
            missing.append('GEMINI_API_KEY')
        if not self.tavily_api_key:
            missing.append('TAVILY_API_KEY')
        return missing


@lru_cache
def get_settings():
    s = Settings()
    s.data_dir.mkdir(parents=True, exist_ok=True)
    return s
