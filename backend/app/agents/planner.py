import json
from app.services.gemini_service import GeminiService

class PlannerAgent:
    def __init__(self, llm=None): self.llm=llm or GeminiService()
    def create_plan(self, question:str, max_tasks:int, geography=None, industry=None):
        instructions="""You are the planning component of a rigorous business research system. Decompose the problem into independent, searchable tasks suitable for parallel execution. Cover market size/demand, customers, competitors, pricing/economics, regulation/constraints, technology/substitutes, opportunities and risks when relevant. Do not assume facts. Return ONLY JSON: {"research_question":str,"decision_frame":str,"tasks":[{"task_id":"T1","topic":str,"research_query":str,"purpose":str,"priority":1-5}]}. Create no more than the requested number of tasks."""
        prompt=f"Question: {question}\nGeography: {geography or 'not specified'}\nIndustry: {industry or 'infer only when obvious'}\nMaximum tasks: {max_tasks}"
        data=self.llm.json(instructions,prompt)
        tasks=data.get('tasks',[])[:max_tasks]
        for i,t in enumerate(tasks,1):
            t['task_id']=f'T{i}'
        data['tasks']=tasks
        data['research_question']=question
        return data
