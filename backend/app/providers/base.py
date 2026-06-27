from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProviderResponse:
    provider: str
    response_text: str
    latency_ms: float
    token_usage: dict
    error: Optional[str] = None


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def generate(self, prompt: str) -> ProviderResponse:
        ...