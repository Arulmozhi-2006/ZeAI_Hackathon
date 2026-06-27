import logging
import time

import google.generativeai as genai

from app.core.config import settings
from app.providers.base import LLMProvider, ProviderResponse

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)

    async def generate(self, prompt: str) -> ProviderResponse:
        t0 = time.time()
        try:
            result = self._model.generate_content(prompt)
            latency_ms = (time.time() - t0) * 1000

            text = (result.text or "").strip() if hasattr(result, "text") else ""

            usage = getattr(result, "usage_metadata", None)
            token_usage = {
                "prompt_tokens": getattr(usage, "prompt_token_count", None),
                "completion_tokens": getattr(usage, "candidates_token_count", None),
                "total_tokens": getattr(usage, "total_token_count", None),
            } if usage else {}

            return ProviderResponse(
                provider=self.name,
                response_text=text,
                latency_ms=latency_ms,
                token_usage=token_usage,
            )
        except Exception as e:
            latency_ms = (time.time() - t0) * 1000
            logger.error(f"Gemini provider error: {e}")
            return ProviderResponse(
                provider=self.name,
                response_text="",
                latency_ms=latency_ms,
                token_usage={},
                error=str(e),
            )
