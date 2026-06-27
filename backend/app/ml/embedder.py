import logging
import time
from functools import lru_cache
from typing import List

import numpy as np

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _load_model(model_name: str):
    """Lazy-load sentence transformer (cached — loads once per process)."""
    logger.info(f"Loading embedding model: {model_name}")
    t0 = time.time()
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name)
    logger.info(f"Embedding model loaded in {time.time() - t0:.2f}s")
    return model


def get_embedding(text: str, model_name: str = "all-MiniLM-L6-v2") -> np.ndarray:
    """Return a 384-dim L2-normalised embedding vector."""
    model = _load_model(model_name)
    vector = model.encode(text, normalize_embeddings=True, show_progress_bar=False)
    return vector.astype(np.float32)


def get_embeddings_batch(texts: List[str], model_name: str = "all-MiniLM-L6-v2") -> np.ndarray:
    """Batch encode for training — shape (N, 384)."""
    model = _load_model(model_name)
    vectors = model.encode(texts, normalize_embeddings=True, batch_size=64, show_progress_bar=True)
    return vectors.astype(np.float32)