import logging
import time
from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

from app.core.config import settings
from app.ml.preprocessor import preprocess_prompt
from app.ml.embedder import get_embedding
from app.ml.features import build_feature_vector, extract_features
from app.ml.classifier import predict, CATEGORY_NAMES
from app.ml.risk_scorer import compute_risk_score, severity_from_score
from app.ml.explainer import explain

logger = logging.getLogger(__name__)

_ARTIFACT_PATH_TPL = "{dir}/xgboost_firewall.joblib"


@dataclass
class DetectionOutput:
    # Core classification
    category_id: int
    category_name: str
    confidence: float
    all_probs: Dict[str, float]

    # Risk
    risk_score: float
    severity: str

    # Explainability
    classification_reason: str
    threat_explanation: str

    # Metadata
    inference_time_ms: float
    embedding_vector: np.ndarray
    model_version: str
    preprocessed_prompt: str
    total_pattern_hits: int


def run_detection(raw_prompt: str) -> DetectionOutput:
    t_start = time.time()

    artifact_path = _ARTIFACT_PATH_TPL.format(dir=settings.MODEL_ARTIFACT_DIR)

    # 1. Preprocess
    clean = preprocess_prompt(raw_prompt)

    # 2. Embed
    embedding = get_embedding(clean, model_name=settings.EMBEDDING_MODEL_NAME)

    # 3. Feature vector
    features = extract_features(clean)
    feature_vector = build_feature_vector(clean, embedding)
    total_pattern_hits = int(features[9])  # index 9 = total_hits

    # 4. Classify
    category_id, confidence, all_probs = predict(feature_vector, artifact_path)
    category_name = CATEGORY_NAMES[category_id - 1]

    # 5. Risk score
    risk_score = compute_risk_score(category_id, confidence, total_pattern_hits, all_probs)
    severity = severity_from_score(risk_score)

    # 6. Explain
    explanations = explain(clean, category_id, confidence, all_probs)

    inference_ms = (time.time() - t_start) * 1000
    logger.info(
        f"Detection: '{category_name}' conf={confidence:.2f} "
        f"risk={risk_score} severity={severity} time={inference_ms:.0f}ms"
    )

    return DetectionOutput(
        category_id=category_id,
        category_name=category_name,
        confidence=confidence,
        all_probs=all_probs,
        risk_score=risk_score,
        severity=severity,
        classification_reason=explanations["classification_reason"],
        threat_explanation=explanations["threat_explanation"],
        inference_time_ms=inference_ms,
        embedding_vector=embedding,
        model_version="xgboost_firewall_v1",
        preprocessed_prompt=clean,
        total_pattern_hits=total_pattern_hits,
    )