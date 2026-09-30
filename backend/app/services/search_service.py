from datetime import datetime, timezone
from tavily import TavilyClient
from app.core.config import get_settings
from app.utils.text import domain_of, source_quality

class SearchService:
    def __init__(self):
        s=get_settings()
        if not s.tavily_api_key:
            raise RuntimeError('TAVILY_API_KEY is missing. Copy .env.example to .env and add it.')
        self.client=TavilyClient(api_key=s.tavily_api_key)
        self.max_chars=s.max_source_chars

    def search(self, query:str, max_results:int=5):
        payload=self.client.search(query=query, search_depth='advanced', max_results=max_results, include_answer=False)
        out=[]
        for i,r in enumerate(payload.get('results', []),1):
            url=r.get('url','')
            out.append({
                'title': r.get('title') or domain_of(url) or 'Untitled source',
                'url': url,
                'domain': domain_of(url),
                'content': (r.get('content') or '')[:self.max_chars],
                'search_score': float(r.get('score') or 0),
                'quality_score': source_quality(url, r.get('title','')),
                'retrieved_at': datetime.now(timezone.utc).isoformat(),
            })
        return out
