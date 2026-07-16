import httpx

from app.core.config import get_settings
from app.services.ai.base import (
    LegalInfoProvider,
    ProviderError,
    SectionFacts,
    build_prompt,
)


class OllamaProvider(LegalInfoProvider):
    """Local LLM via Ollama (https://ollama.com) — free, runs offline."""

    name = "ollama"

    def generate(self, facts: SectionFacts | None, query: str) -> str:
        settings = get_settings()
        system, user = build_prompt(facts, query)
        try:
            response = httpx.post(
                f"{settings.ollama_base_url}/api/chat",
                json={
                    "model": settings.ollama_model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "stream": False,
                },
                timeout=settings.ai_timeout_seconds,
            )
            response.raise_for_status()
            content = response.json()["message"]["content"]
        except (httpx.HTTPError, KeyError) as exc:
            raise ProviderError(f"Ollama request failed: {exc}") from exc
        if not content.strip():
            raise ProviderError("Ollama returned an empty response")
        return content.strip()
