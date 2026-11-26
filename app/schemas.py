from typing import Literal
from pydantic import BaseModel, Field

class ForecastRequest(BaseModel):
    company: Literal['TCS'] = 'TCS'
    quarters: int = Field(3, ge=2, le=3)
    query: str = Field('Analyze business outlook for the upcoming quarter.', min_length=5, max_length=2000)

class Metric(BaseModel):
    name: Literal['revenue_from_operations','net_profit','operating_margin']
    value: float | None
    unit: Literal['INR crore','percent']
    page: int | None
    quote: str | None

class Extraction(BaseModel):
    metrics: list[Metric]

class Claim(BaseModel):
    text: str
    evidence_ids: list[str] = Field(min_length=1)

class Outlook(BaseModel):
    financial_trends: list[Claim] = Field(min_length=1)
    management_sentiment: Claim
    recurring_themes: list[Claim]
    management_outlook: list[Claim]
    revenue_outlook: Claim
    margin_outlook: Claim
    risks: list[Claim]
    opportunities: list[Claim]
    base_case: Claim
    confidence: Literal['low','medium','high']
    confidence_rationale: str
    limitations: list[str]
