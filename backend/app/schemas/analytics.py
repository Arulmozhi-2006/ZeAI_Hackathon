from typing import List, Optional
from datetime import date as date_type

from pydantic import BaseModel


class OverviewStats(BaseModel):
    total_requests: int
    total_allowed: int
    total_blocked: int
    block_rate: float
    avg_risk_score: float
    avg_confidence_score: float
    avg_inference_time_ms: float


class CategoryBreakdown(BaseModel):
    category_id: int
    category_name: str
    count: int
    percentage: float
    avg_risk_score: float


class TrendPoint(BaseModel):
    date: date_type
    total_requests: int
    total_allowed: int
    total_blocked: int
    avg_risk_score: float


class SeverityBreakdown(BaseModel):
    severity: str
    count: int


class ModelMetrics(BaseModel):
    model_version: str
    total_predictions: int
    avg_confidence: float
    avg_inference_time_ms: float
    category_distribution: List[CategoryBreakdown]