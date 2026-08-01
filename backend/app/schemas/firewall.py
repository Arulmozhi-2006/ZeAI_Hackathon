from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    prompt: str
    provider: str = "gemini"


class AnalyzeResponse(BaseModel):
    prompt_log_id: UUID
    decision: str
    category: str
    risk_score: float
    severity: str
    confidence: float
    classification_reason: str
    threat_explanation: str
    policy_rule_triggered: str
    decision_reason: str
    flagged: bool
    llm_response: Optional[str] = None
    llm_provider: Optional[str] = None
    llm_error: Optional[str] = None
    latency_ms: Optional[float] = None