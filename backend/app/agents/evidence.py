import json
from app.services.gemini_service import GeminiService

class EvidenceAgent:
    def __init__(self, llm=None): self.llm=llm or GeminiService()

    def extract_claims(self, task, sources):
        docs=[{'source_id':s['source_id'],'title':s['title'],'domain':s['domain'],'content':s['content']} for s in sources]
        instructions="""Extract only factual, decision-relevant claims explicitly supported by the supplied source excerpts. Do not use outside knowledge. Every claim MUST cite one or more supplied source_id values. Prefer measurable facts, dates, market signals, competitor actions, customer evidence, pricing/economic facts, regulatory facts, and risks. If sources do not support a claim, omit it. Return ONLY JSON: {"claims":[{"claim":str,"source_ids":[str],"evidence_type":"fact|metric|trend|risk|opportunity","importance":1-5}]}. Maximum 7 claims."""
        prompt=f"Task: {json.dumps(task)}\nSources: {json.dumps(docs)}"
        data=self.llm.json(instructions,prompt)
        valid_ids={s['source_id'] for s in sources}
        out=[]
        for c in data.get('claims',[])[:7]:
            ids=[x for x in c.get('source_ids',[]) if x in valid_ids]
            if c.get('claim') and ids:
                c['source_ids']=ids
                c['task_id']=task['task_id']; c['topic']=task['topic']
                out.append(c)
        return out

    def verify_claims(self, claims, sources):
        if not claims: return []
        docs=[{'source_id':s['source_id'],'title':s['title'],'content':s['content']} for s in sources]
        compact=[{'claim_id':f'C{i+1}','claim':c['claim'],'proposed_source_ids':c['source_ids']} for i,c in enumerate(claims)]
        instructions="""Act as a strict evidence verifier. Judge whether each claim is supported by the supplied excerpts. Do not use outside knowledge. A claim is supported only when the excerpt directly entails it; partial or ambiguous evidence is uncertain. Return ONLY JSON: {"verification":[{"claim_id":str,"status":"supported|contradicted|uncertain","supporting_source_ids":[str],"reason":str}]}. Cite only source IDs whose excerpts directly support the claim."""
        data=self.llm.json(instructions, f"Claims: {json.dumps(compact)}\nSources: {json.dumps(docs)}")
        by_id={f'C{i+1}':c for i,c in enumerate(claims)}
        valid_ids={s['source_id'] for s in sources}
        results=[]
        for v in data.get('verification',[]):
            c=by_id.get(v.get('claim_id'))
            if not c: continue
            ids=[x for x in v.get('supporting_source_ids',[]) if x in valid_ids]
            x=dict(c); x['verification_status']=v.get('status','uncertain'); x['source_ids']=ids; x['verification_reason']=v.get('reason','')
            results.append(x)
        return results
