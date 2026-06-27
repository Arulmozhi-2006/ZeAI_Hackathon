"""
Core orchestration: persist prompt -> run detection -> evaluate policy
-> (maybe) call LLM provider -> persist everything -> return unified result.
"""
import hashlib
import logging
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.ml.engine import run_detection, DetectionOutput
from app.models.prompt_log import PromptLog, PromptStatus
from app.models.model_prediction import ModelPrediction
from app.models.detection_result import DetectionResult
from app.models.firewall_decision import FirewallDecision, DecisionType
from app.models.threat_log import ThreatLog, SeverityLevel
from app.models.llm_response import LLMResponse
from app.providers.factory import get_provider
from app.services.policy_engine import evaluate_policy

logger = logging.getLogger(__name__)


@dataclass
class FirewallResult:
    prompt_log_id: UUID
    decision: str                  # ALLOW | BLOCK
    category_name: str
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
    latency_ms: Optional[float] = None


def _hash_prompt(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


async def process_prompt(
    db: Session,
    user_id: UUID,
    raw_prompt: str,
    api_key_id: Optional[UUID] = None,
    source_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    provider_name: str = "gemini",
) -> FirewallResult:
    # 1. Persist prompt_log (PENDING)
    prompt_log = PromptLog(
        user_id=user_id,
        api_key_id=api_key_id,
        raw_prompt=raw_prompt,
        prompt_hash=_hash_prompt(raw_prompt),
        source_ip=source_ip,
        user_agent=user_agent,
        status=PromptStatus.PENDING,
    )
    db.add(prompt_log)
    db.commit()
    db.refresh(prompt_log)

    try:
        # 2-7. Run full detection pipeline
        detection: DetectionOutput = run_detection(raw_prompt)

        # 8. Persist model_predictions
        model_prediction = ModelPrediction(
            prompt_log_id=prompt_log.id,
            model_version=detection.model_version,
            embedding_vector=detection.embedding_vector.tolist(),
            predicted_category_id=detection.category_id,
            confidence_score=detection.confidence,
            raw_model_output=detection.all_probs,
            inference_time_ms=detection.inference_time_ms,
        )
        db.add(model_prediction)
        db.commit()
        db.refresh(model_prediction)

        # 9. Persist detection_results
        detection_result = DetectionResult(
            prompt_log_id=prompt_log.id,
            model_prediction_id=model_prediction.id,
            final_category_id=detection.category_id,
            risk_score=detection.risk_score,
            classification_reason=detection.classification_reason,
            threat_explanation=detection.threat_explanation,
        )
        db.add(detection_result)
        db.commit()
        db.refresh(detection_result)

        # 10. Policy decision
        verdict = evaluate_policy(detection.category_id, detection.category_name, detection.risk_score)

        llm_response_text = None
        llm_provider_used = None
        latency_ms = None

        # 11a/11b. Forward to LLM if ALLOW
        if verdict.decision == "ALLOW":
            provider = get_provider(provider_name)
            result = await provider.generate(raw_prompt)
            llm_response_text = result.response_text
            llm_provider_used = result.provider
            latency_ms = result.latency_ms

            db.add(LLMResponse(
                prompt_log_id=prompt_log.id,
                provider=result.provider,
                response_text=result.response_text,
                latency_ms=result.latency_ms,
                token_usage=result.token_usage,
            ))

        # 12. Persist firewall_decisions
        db.add(FirewallDecision(
            prompt_log_id=prompt_log.id,
            detection_result_id=detection_result.id,
            decision=DecisionType.ALLOW if verdict.decision == "ALLOW" else DecisionType.BLOCK,
            policy_rule_triggered=verdict.policy_rule_triggered,
            decision_reason=verdict.decision_reason,
            llm_provider=llm_provider_used,
            llm_forwarded=verdict.decision == "ALLOW",
        ))

        # 13. Persist threat_logs
        db.add(ThreatLog(
            prompt_log_id=prompt_log.id,
            threat_category_id=detection.category_id,
            severity=SeverityLevel[detection.severity],
            risk_score=detection.risk_score,
            blocked=verdict.decision == "BLOCK",
        ))

        # Mark prompt as processed
        prompt_log.status = PromptStatus.PROCESSED
        db.commit()

        return FirewallResult(
            prompt_log_id=prompt_log.id,
            decision=verdict.decision,
            category_name=detection.category_name,
            risk_score=detection.risk_score,
            severity=detection.severity,
            confidence=detection.confidence,
            classification_reason=detection.classification_reason,
            threat_explanation=detection.threat_explanation,
            policy_rule_triggered=verdict.policy_rule_triggered,
            decision_reason=verdict.decision_reason,
            flagged=verdict.flagged,
            llm_response=llm_response_text,
            llm_provider=llm_provider_used,
            latency_ms=latency_ms,
        )

    except Exception as e:
        logger.exception(f"Error processing prompt {prompt_log.id}: {e}")
        prompt_log.status = PromptStatus.ERROR
        db.commit()
        raise