from typing import Optional, List
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class PromptLogRead(BaseModel):
    id: UUID
    raw_prompt: str
    prompt_hash: str
    source_ip: Optional[str]
    user_agent: Optional[str]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ThreatLogRead(BaseModel):
    id: UUID
    prompt_log_id: UUID
    threat_category_id: int
    category_name: Optional[str] = None
    severity: str
    risk_score: float
    blocked: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DetectionDetailRead(BaseModel):
    prompt_log_id: UUID
    raw_prompt: str
    category_name: str
    confidence_score: float
    risk_score: float
    severity: str
    decision: str
    policy_rule_triggered: str
    classification_reason: str
    threat_explanation: str
    llm_provider: Optional[str] = None
    llm_response: Optional[str] = None
    created_at: datetime


class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    page_size: int