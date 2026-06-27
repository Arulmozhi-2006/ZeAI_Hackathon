"""
XGBoost multi-class threat classifier.
Input:  384-dim embedding + 20 lexical features = 404-dim vector
Output: threat_category_id (int) + per-class probabilities
"""
import logging
import os
import time
from functools import lru_cache
from typing import Tuple, Dict

import joblib
import numpy as np

logger = logging.getLogger(__name__)

CATEGORY_NAMES = [
    "Safe",
    "Suspicious",
    "Prompt Injection",
    "Jailbreak",
    "Indirect Injection",
    "Data Exfiltration",
    "Privilege Escalation",
    "System Prompt Theft",
]

# category_id → 0-indexed label (matches DB seed order: id=1..8)
LABEL_TO_CATEGORY_ID = {i: i + 1 for i in range(len(CATEGORY_NAMES))}
CATEGORY_ID_TO_LABEL = {v: k for k, v in LABEL_TO_CATEGORY_ID.items()}


@lru_cache(maxsize=1)
def _load_classifier(artifact_path: str):
    if not os.path.exists(artifact_path):
        raise FileNotFoundError(
            f"Classifier artifact not found at {artifact_path}. "
            "Run backend/app/ml/trainer.py first."
        )
    logger.info(f"Loading XGBoost classifier from {artifact_path}")
    return joblib.load(artifact_path)


def predict(
    feature_vector: np.ndarray,
    artifact_path: str,
) -> Tuple[int, float, Dict[str, float]]:
    """
    Returns:
        category_id  (int)   — 1-indexed DB category id
        confidence   (float) — probability of winning class
        all_probs    (dict)  — {category_name: probability}
    """
    t0 = time.time()
    clf = _load_classifier(artifact_path)

    X = feature_vector.reshape(1, -1)
    proba = clf.predict_proba(X)[0]  # shape (8,)
    label = int(np.argmax(proba))
    confidence = float(proba[label])
    category_id = LABEL_TO_CATEGORY_ID[label]

    all_probs = {CATEGORY_NAMES[i]: float(proba[i]) for i in range(len(CATEGORY_NAMES))}

    elapsed_ms = (time.time() - t0) * 1000
    logger.debug(
        f"Classifier: label={CATEGORY_NAMES[label]} conf={confidence:.3f} "
        f"time={elapsed_ms:.1f}ms"
    )
    return category_id, confidence, all_probs