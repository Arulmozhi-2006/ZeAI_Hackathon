"""
Generates human-readable classification reasons and threat explanations
from the matched patterns and model output.
"""
from typing import Dict, List

from app.ml.classifier import CATEGORY_NAMES
from app.ml.features import get_matched_patterns

_CATEGORY_EXPLANATIONS = {
    1: "The prompt appears safe with no detected adversarial indicators.",
    2: "The prompt contains anomalous patterns but no definitive attack signature. Forwarded with caution flag.",
    3: "A direct prompt injection was detected. The prompt attempts to override or supplant the system instructions.",
    4: "A jailbreak attempt was detected. The prompt tries to bypass the model's safety constraints or ethical guidelines.",
    5: "An indirect injection pattern was detected. The prompt may carry malicious instructions embedded in external content.",
    6: "A data exfiltration attempt was detected. The prompt attempts to extract sensitive data, credentials, or system information.",
    7: "A privilege escalation attempt was detected. The prompt attempts to gain elevated permissions or impersonate privileged roles.",
    8: "A system prompt theft attempt was detected. The prompt attempts to reveal or extract the system-level instructions.",
}

_PATTERN_LABELS = {
    "injection": "Direct injection keyword",
    "jailbreak": "Jailbreak keyword",
    "exfiltration": "Data exfiltration pattern",
    "privilege": "Privilege escalation keyword",
    "indirect": "Indirect/structural injection pattern",
}


def build_classification_reason(
    category_id: int,
    confidence: float,
    matched_patterns: Dict[str, list],
    top_probs: Dict[str, float],
) -> str:
    category_name = CATEGORY_NAMES[category_id - 1]
    lines = [f"Classified as '{category_name}' (confidence: {confidence:.1%})."]

    if matched_patterns:
        pattern_summary = "; ".join(
            f"{_PATTERN_LABELS.get(k, k)}: {len(v)} match(es)"
            for k, v in matched_patterns.items()
        )
        lines.append(f"Pattern signals: {pattern_summary}.")

    # Show top 3 competing classes
    sorted_probs = sorted(top_probs.items(), key=lambda x: x[1], reverse=True)[:3]
    top_str = ", ".join(f"{name} ({prob:.1%})" for name, prob in sorted_probs)
    lines.append(f"Top predictions: {top_str}.")

    return " ".join(lines)


def build_threat_explanation(
    category_id: int,
    matched_patterns: Dict[str, list],
) -> str:
    base = _CATEGORY_EXPLANATIONS.get(category_id, "Unknown threat category.")
    if not matched_patterns:
        return base

    details = []
    for bank, patterns in matched_patterns.items():
        # Show first matched pattern string as example
        example = patterns[0][:80] + "…" if len(patterns[0]) > 80 else patterns[0]
        details.append(f"[{_PATTERN_LABELS.get(bank, bank)}] e.g. `{example}`")

    return base + " Matched indicators: " + " | ".join(details)


def explain(
    text: str,
    category_id: int,
    confidence: float,
    all_probs: Dict[str, float],
) -> Dict[str, str]:
    matched = get_matched_patterns(text)
    return {
        "classification_reason": build_classification_reason(
            category_id, confidence, matched, all_probs
        ),
        "threat_explanation": build_threat_explanation(category_id, matched),
    }