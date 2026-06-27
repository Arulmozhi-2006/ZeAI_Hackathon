"""
Read-time aggregation queries over the log tables.
No materialized views needed at hackathon scale — plain SQL aggregates
are fast enough and stay simple to reason about / demo.
"""
import logging
from datetime import date, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.models.detection_result import DetectionResult
from app.models.firewall_decision import FirewallDecision, DecisionType
from app.models.model_prediction import ModelPrediction
from app.models.prompt_log import PromptLog
from app.models.threat_category import ThreatCategory
from app.models.threat_log import ThreatLog

logger = logging.getLogger(__name__)


def get_overview(db: Session, user_id: Optional[UUID] = None, days: int = 30) -> dict:
    since = date.today() - timedelta(days=days)

    q = (
        db.query(
            func.count(PromptLog.id).label("total_requests"),
            func.sum(case((FirewallDecision.decision == DecisionType.ALLOW, 1), else_=0)).label("allowed"),
            func.sum(case((FirewallDecision.decision == DecisionType.BLOCK, 1), else_=0)).label("blocked"),
        )
        .join(FirewallDecision, FirewallDecision.prompt_log_id == PromptLog.id)
        .filter(PromptLog.created_at >= since)
    )
    if user_id:
        q = q.filter(PromptLog.user_id == user_id)
    row = q.first()

    total = row.total_requests or 0
    allowed = row.allowed or 0
    blocked = row.blocked or 0

    risk_q = db.query(func.avg(DetectionResult.risk_score)).join(
        PromptLog, PromptLog.id == DetectionResult.prompt_log_id
    ).filter(PromptLog.created_at >= since)
    if user_id:
        risk_q = risk_q.filter(PromptLog.user_id == user_id)
    avg_risk = risk_q.scalar() or 0.0

    conf_q = db.query(func.avg(ModelPrediction.confidence_score)).join(
        PromptLog, PromptLog.id == ModelPrediction.prompt_log_id
    ).filter(PromptLog.created_at >= since)
    if user_id:
        conf_q = conf_q.filter(PromptLog.user_id == user_id)
    avg_confidence = conf_q.scalar() or 0.0

    time_q = db.query(func.avg(ModelPrediction.inference_time_ms)).join(
        PromptLog, PromptLog.id == ModelPrediction.prompt_log_id
    ).filter(PromptLog.created_at >= since)
    if user_id:
        time_q = time_q.filter(PromptLog.user_id == user_id)
    avg_inference = time_q.scalar() or 0.0

    return {
        "total_requests": total,
        "total_allowed": allowed,
        "total_blocked": blocked,
        "block_rate": round((blocked / total * 100), 2) if total else 0.0,
        "avg_risk_score": round(float(avg_risk), 2),
        "avg_confidence_score": round(float(avg_confidence), 4),
        "avg_inference_time_ms": round(float(avg_inference), 2),
    }


def get_category_breakdown(db: Session, user_id: Optional[UUID] = None, days: int = 30) -> List[dict]:
    since = date.today() - timedelta(days=days)

    q = (
        db.query(
            ThreatCategory.id,
            ThreatCategory.name,
            func.count(ThreatLog.id).label("count"),
            func.avg(ThreatLog.risk_score).label("avg_risk"),
        )
        .join(ThreatLog, ThreatLog.threat_category_id == ThreatCategory.id)
        .join(PromptLog, PromptLog.id == ThreatLog.prompt_log_id)
        .filter(PromptLog.created_at >= since)
        .group_by(ThreatCategory.id, ThreatCategory.name)
    )
    if user_id:
        q = q.filter(PromptLog.user_id == user_id)

    rows = q.all()
    total = sum(r.count for r in rows) or 1

    return [
        {
            "category_id": r.id,
            "category_name": r.name,
            "count": r.count,
            "percentage": round(r.count / total * 100, 2),
            "avg_risk_score": round(float(r.avg_risk or 0), 2),
        }
        for r in rows
    ]


def get_severity_breakdown(db: Session, user_id: Optional[UUID] = None, days: int = 30) -> List[dict]:
    since = date.today() - timedelta(days=days)
    q = (
        db.query(ThreatLog.severity, func.count(ThreatLog.id).label("count"))
        .join(PromptLog, PromptLog.id == ThreatLog.prompt_log_id)
        .filter(PromptLog.created_at >= since)
        .group_by(ThreatLog.severity)
    )
    if user_id:
        q = q.filter(PromptLog.user_id == user_id)
    return [{"severity": r.severity.value, "count": r.count} for r in q.all()]


def get_trends(db: Session, user_id: Optional[UUID] = None, days: int = 14) -> List[dict]:
    since = date.today() - timedelta(days=days)

    q = (
        db.query(
            func.date(PromptLog.created_at).label("day"),
            func.count(PromptLog.id).label("total"),
            func.sum(case((FirewallDecision.decision == DecisionType.ALLOW, 1), else_=0)).label("allowed"),
            func.sum(case((FirewallDecision.decision == DecisionType.BLOCK, 1), else_=0)).label("blocked"),
            func.avg(DetectionResult.risk_score).label("avg_risk"),
        )
        .join(FirewallDecision, FirewallDecision.prompt_log_id == PromptLog.id)
        .outerjoin(DetectionResult, DetectionResult.prompt_log_id == PromptLog.id)
        .filter(PromptLog.created_at >= since)
        .group_by(func.date(PromptLog.created_at))
        .order_by(func.date(PromptLog.created_at))
    )
    if user_id:
        q = q.filter(PromptLog.user_id == user_id)

    return [
        {
            "date": r.day,
            "total_requests": r.total,
            "total_allowed": r.allowed or 0,
            "total_blocked": r.blocked or 0,
            "avg_risk_score": round(float(r.avg_risk or 0), 2),
        }
        for r in q.all()
    ]


def get_model_metrics(db: Session) -> dict:
    row = db.query(
        func.count(ModelPrediction.id).label("total"),
        func.avg(ModelPrediction.confidence_score).label("avg_conf"),
        func.avg(ModelPrediction.inference_time_ms).label("avg_time"),
    ).first()

    latest_version_row = (
        db.query(ModelPrediction.model_version)
        .order_by(ModelPrediction.created_at.desc())
        .first()
    )
    model_version = latest_version_row[0] if latest_version_row else "unknown"

    category_dist = (
        db.query(
            ThreatCategory.id,
            ThreatCategory.name,
            func.count(ModelPrediction.id).label("count"),
            func.avg(ModelPrediction.confidence_score).label("avg_conf"),
        )
        .join(ModelPrediction, ModelPrediction.predicted_category_id == ThreatCategory.id)
        .group_by(ThreatCategory.id, ThreatCategory.name)
        .all()
    )
    total = row.total or 1

    return {
        "model_version": model_version,
        "total_predictions": row.total or 0,
        "avg_confidence": round(float(row.avg_conf or 0), 4),
        "avg_inference_time_ms": round(float(row.avg_time or 0), 2),
        "category_distribution": [
            {
                "category_id": c.id,
                "category_name": c.name,
                "count": c.count,
                "percentage": round(c.count / total * 100, 2),
                "avg_risk_score": round(float(c.avg_conf or 0), 4),
            }
            for c in category_dist
        ],
    }
