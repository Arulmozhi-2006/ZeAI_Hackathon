import logging
from functools import lru_cache

from app.providers.base import LLMProvider
from app.providers.gemini import GeminiProvider

logger = logging.getLogger(__name__)

_REGISTRY = {
    "gemini": GeminiProvider,
}


@lru_cache(maxsize=4)
def get_provider(name: str = "gemini") -> LLMProvider:
    provider_cls = _REGISTRY.get(name)
    if not provider_cls:
        logger.warning(f"Unknown provider '{name}', falling back to gemini")
        provider_cls = _REGISTRY["gemini"]
    return provider_cls()