"""
Policy Engine — converts a DetectionOutput into an ALLOW/BLOCK decision.

Rules (evaluated in order, first match wins):
  1. risk_score >= RISK_BLOCK_THRESHOLD          -> BLOCK
  2. category in HARD_BLOCK_CATEGORIES           -> BLOCK (regardless of score)
  3. category == Suspicious                      -> ALLOW (flagged)
  4. otherwise                                   -> ALLOW
"""
import logging
from dataclasses import dataclass
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# Category IDs that are always blocked regardless of risk score
HARD_BLOCK_CATEGORIES = {
    3: "Prompt Injection",
    4: "Jailbreak",
    5: "Indirect Injection",
    6: "Data Exfiltration",
    7: "Privilege Escalation",
    8: "System Prompt Theft",
}

SUSPICIOUS_CATEGORY_ID = 2
SAFE_CATEGORY_ID = 1


@dataclass
class PolicyVerdict:
    decision: str            # "ALLOW" | "BLOCK"
    policy_rule_triggered: str
    decision_reason: str
    flagged: bool = False    # ALLOW but worth surfacing in dashboard


def evaluate_policy(category_id: int, category_name: str, risk_score: float) -> PolicyVerdict:
    # Rule 1 — risk threshold
    if risk_score >= settings.RISK_BLOCK_THRESHOLD:
        return PolicyVerdict(
            decision="BLOCK",
            policy_rule_triggered=f"RISK_SCORE_THRESHOLD(>={settings.RISK_BLOCK_THRESHOLD})",
            decision_reason=(
                f"Risk score {risk_score:.1f} meets or exceeds the block threshold "
                f"of {settings.RISK_BLOCK_THRESHOLD}."
            ),
        )

    # Rule 2 — hard-block categories regardless of score
    if category_id in HARD_BLOCK_CATEGORIES:
        return PolicyVerdict(
            decision="BLOCK",
            policy_rule_triggered=f"HARD_BLOCK_CATEGORY({category_name})",
            decision_reason=(
                f"Category '{category_name}' is in the hard-block list and is "
                f"blocked irrespective of risk score (score={risk_score:.1f})."
            ),
        )

    # Rule 3 — suspicious: allow but flag
    if category_id == SUSPICIOUS_CATEGORY_ID:
        return PolicyVerdict(
            decision="ALLOW",
            policy_rule_triggered="SUSPICIOUS_ALLOW_WITH_FLAG",
            decision_reason=(
                f"Category 'Suspicious' with risk score {risk_score:.1f} is below "
                "block threshold; forwarded to LLM with monitoring flag."
            ),
            flagged=True,
        )

    # Rule 4 — default allow (Safe)
    return PolicyVerdict(
        decision="ALLOW",
        policy_rule_triggered="DEFAULT_ALLOW",
        decision_reason=f"Category '{category_name}' classified as safe (risk={risk_score:.1f}).",
    )