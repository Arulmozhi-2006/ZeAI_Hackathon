"""
Risk Scoring Engine.
Produces a composite risk score in [0, 100] from:
  - ML model confidence
  - Category base severity
  - Lexical pattern signal strength
"""
from typing import Dict

CATEGORY_SEVERITY_WEIGHTS = {
    1: 0.0,    # Safe
    2: 0.25,   # Suspicious
    3: 0.75,   # Prompt Injection
    4: 0.80,   # Jailbreak
    5: 0.75,   # Indirect Injection
    6: 0.95,   # Data Exfiltration
    7: 0.90,   # Privilege Escalation
    8: 0.80,   # System Prompt Theft
}

# Weights for score components
_W_CONFIDENCE = 0.50
_W_SEVERITY = 0.35
_W_PATTERN = 0.15
_PATTERN_CAP = 10  # saturates at 10 pattern hits → 1.0 signal


def compute_risk_score(
    category_id: int,
    confidence: float,
    total_pattern_hits: int,
    all_probs: Dict[str, float],
) -> float:
    """
    Returns composite risk score 0–100.

    - confidence:         model probability of predicted class (0–1)
    - severity_weight:    category-specific base risk (0–1)
    - pattern_signal:     normalised pattern hit count (0–1)
    """
    severity_weight = CATEGORY_SEVERITY_WEIGHTS.get(category_id, 0.5)

    # Weighted average of all malicious class probs (categories 3-8)
    malicious_mass = sum(
        prob for i, prob in enumerate(all_probs.values()) if i >= 2
    )

    pattern_signal = min(total_pattern_hits / _PATTERN_CAP, 1.0)

    raw_score = (
        _W_CONFIDENCE * (confidence if category_id >= 3 else malicious_mass) +
        _W_SEVERITY   * severity_weight +
        _W_PATTERN    * pattern_signal
    )

    return round(min(max(raw_score * 100, 0.0), 100.0), 2)


def severity_from_score(risk_score: float) -> str:
    if risk_score >= 80:
        return "CRITICAL"
    elif risk_score >= 60:
        return "HIGH"
    elif risk_score >= 35:
        return "MEDIUM"
    else:
        return "LOW"