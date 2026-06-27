from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.detection_result import DetectionResult
from app.models.firewall_decision import FirewallDecision
from app.models.llm_response import LLMResponse
from app.models.model_prediction import ModelPrediction
from app.models.prompt_log import PromptLog
from app.models.threat_category import ThreatCategory
from app.models.threat_log import ThreatLog


def get_prompt_logs(db: Session, user_id: Optional[UUID], page: int, page_size: int):
    q = db.query(PromptLog).order_by(PromptLog.created_at.desc())
    if user_id:
        q = q.filter(PromptLog.user_id == user_id)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_threat_logs(db: Session, user_id: Optional[UUID], severity: Optional[str], page: int, page_size: int):
    q = (
        db.query(ThreatLog, ThreatCategory.name)
        .join(ThreatCategory, ThreatCategory.id == ThreatLog.threat_category_id)
        .join(PromptLog, PromptLog.id == ThreatLog.prompt_log_id)
        .order_by(ThreatLog.created_at.desc())
    )
    if user_id:
        q = q.filter(PromptLog.user_id == user_id)
    if severity:
        q = q.filter(ThreatLog.severity == severity)
    total = q.count()
    rows = q.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for threat_log, category_name in rows:
        items.append({
            "id": threat_log.id,
            "prompt_log_id": threat_log.prompt_log_id,
            "threat_category_id": threat_log.threat_category_id,
            "category_name": category_name,
            "severity": threat_log.severity.value,
            "risk_score": threat_log.risk_score,
            "blocked": threat_log.blocked,
            "created_at": threat_log.created_at,
        })
    return items, total


def get_detection_detail(db: Session, prompt_log_id: UUID, user_id: Optional[UUID] = None):
    q = (
        db.query(
            PromptLog,
            DetectionResult,
            ModelPrediction,
            ThreatCategory.name,
            FirewallDecision,
            LLMResponse,
        )
        .join(DetectionResult, DetectionResult.prompt_log_id == PromptLog.id)
        .join(ModelPrediction, ModelPrediction.id == DetectionResult.model_prediction_id)
        .join(ThreatCategory, ThreatCategory.id == DetectionResult.final_category_id)
        .outerjoin(FirewallDecision, FirewallDecision.prompt_log_id == PromptLog.id)
        .outerjoin(LLMResponse, LLMResponse.prompt_log_id == PromptLog.id)
        .filter(PromptLog.id == prompt_log_id)
    )
    if user_id:
        q = q.filter(PromptLog.user_id == user_id)

    row = q.first()
    if not row:
        return None

    prompt_log, detection_result, model_prediction, category_name, firewall_decision, llm_response = row

    return {
        "prompt_log_id": prompt_log.id,
        "raw_prompt": prompt_log.raw_prompt,
        "category_name": category_name,
        "confidence_score": model_prediction.confidence_score,
        "risk_score": detection_result.risk_score,
        "severity": _severity_from_score(detection_result.risk_score),
        "decision": firewall_decision.decision.value if firewall_decision else "UNKNOWN",
        "policy_rule_triggered": firewall_decision.policy_rule_triggered if firewall_decision else "",
        "classification_reason": detection_result.classification_reason,
        "threat_explanation": detection_result.threat_explanation,
        "llm_provider": firewall_decision.llm_provider if firewall_decision else None,
        "llm_response": llm_response.response_text if llm_response else None,
        "created_at": prompt_log.created_at,
    }


def _severity_from_score(score: float) -> str:
    if score >= 80:
        return "CRITICAL"
    elif score >= 60:
        return "HIGH"
    elif score >= 35:
        return "MEDIUM"
    return "LOW"