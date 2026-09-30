import json, sqlite3, threading
from datetime import datetime, timezone
from app.core.config import get_settings

class Repository:
    def __init__(self):
        self.path=get_settings().db_path; self.lock=threading.Lock(); self._init()
    def _conn(self):
        c=sqlite3.connect(self.path, check_same_thread=False); c.row_factory=sqlite3.Row; return c
    def _init(self):
        with self._conn() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, question TEXT NOT NULL, status TEXT NOT NULL, stage TEXT NOT NULL, progress INTEGER NOT NULL, error TEXT, request_json TEXT, result_json TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""")
    def create(self, rid, question, request):
        now=datetime.now(timezone.utc).isoformat()
        with self.lock,self._conn() as c: c.execute('INSERT INTO jobs VALUES (?,?,?,?,?,?,?,?,?,?)',(rid,question,'queued','Queued',0,None,json.dumps(request),None,now,now))
    def update(self,rid,**kwargs):
        allowed={'status','stage','progress','error','result_json'}; data={k:v for k,v in kwargs.items() if k in allowed}; data['updated_at']=datetime.now(timezone.utc).isoformat()
        sets=', '.join(f'{k}=?' for k in data); vals=list(data.values())+[rid]
        with self.lock,self._conn() as c: c.execute(f'UPDATE jobs SET {sets} WHERE id=?',vals)
    def get(self,rid):
        with self._conn() as c: row=c.execute('SELECT * FROM jobs WHERE id=?',(rid,)).fetchone()
        if not row: return None
        d=dict(row); d['result']=json.loads(d['result_json']) if d.get('result_json') else None; d['request']=json.loads(d['request_json']) if d.get('request_json') else None; return d
