from app.core.config import get_settings
from app.mapreduce.local_engine import LocalMapReduceEngine
from app.mapreduce.hadoop_engine import HadoopStreamingEngine

def get_mapreduce_engine():
    s=get_settings()
    if s.hadoop_mode=='streaming': return HadoopStreamingEngine()
    if s.hadoop_mode=='auto' and HadoopStreamingEngine.available(): return HadoopStreamingEngine()
    return LocalMapReduceEngine(s.research_workers)
