import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_flexible
from app.db.session import get_db
from app.models.user import User
from app.schemas.firewall import AnalyzeRequest, AnalyzeResponse
from app.services.audit_service import log_action
from app.services.firewall_service import process_prompt
from app.middleware.rate_limiter import check_rate_limit

router = APIRouter(prefix="/firewall", tags=["firewall"])  # ← MUST HAVE THIS
logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    data: AnalyzeRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_flexible),
):
    check_rate_limit(db, current_user.id)
    
    result = await process_prompt(
        db=db,
        user_id=current_user.id,
        raw_prompt=data.prompt,
        source_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        provider_name=data.provider,
    )

    log_action(
        db,
        action_type="FIREWALL_ANALYZE",
        user_id=current_user.id,
        resource_type="prompt_log",
        resource_id=str(result.prompt_log_id),
        ip_address=request.client.host if request.client else None,
        metadata={"decision": result.decision, "risk_score": result.risk_score},
    )

    return AnalyzeResponse(
        prompt_log_id=result.prompt_log_id,
        decision=result.decision,
        category=result.category_name,
        risk_score=result.risk_score,
        severity=result.severity,
        confidence=result.confidence,
        classification_reason=result.classification_reason,
        threat_explanation=result.threat_explanation,
        policy_rule_triggered=result.policy_rule_triggered,
        decision_reason=result.decision_reason,
        flagged=result.flagged,
        hard_blocked=getattr(result, 'hard_blocked', False),
        hard_block_reason=getattr(result, 'hard_block_reason', None),
        llm_response=result.llm_response,
        llm_provider=result.llm_provider,
        latency_ms=result.latency_ms,
    )