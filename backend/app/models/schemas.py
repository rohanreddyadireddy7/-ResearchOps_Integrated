from typing import Any, Optional
from pydantic import BaseModel, Field


class HistoricalPoint(BaseModel):
    year: int
    value: float = Field(gt=0)


class ResearchRequest(BaseModel):
    question: str = Field(min_length=8, max_length=4000)
    geography: Optional[str] = None
    industry: Optional[str] = None
    max_tasks: int = Field(default=6, ge=3, le=12)
    sources_per_task: int = Field(default=5, ge=2, le=10)
    baseline_value: Optional[float] = Field(default=None, gt=0)
    historical_data: list[HistoricalPoint] = Field(default_factory=list)
    forecast_years: int = Field(default=5, ge=1, le=5)
    include_decision_suggestion: bool = False
    decision_style: str = Field(default='Balanced', max_length=60)


class ResearchAccepted(BaseModel):
    research_id: str
    status: str


class JobStatus(BaseModel):
    research_id: str
    status: str
    stage: str
    progress: int
    error: Optional[str] = None
    result: Optional[dict[str, Any]] = None
