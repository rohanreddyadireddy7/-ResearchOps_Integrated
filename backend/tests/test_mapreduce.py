from app.mapreduce.local_engine import LocalMapReduceEngine

def test_mapreduce():
    docs=[{'topic':'Market','domain':'a.com','content':'growth demand growth risk competition'}, {'topic':'Market','domain':'b.com','content':'demand expansion'}]
    out=LocalMapReduceEngine(2).run(docs)
    assert out['Market']['documents']==2
    assert dict(out['Market']['top_terms'])['growth']==2
