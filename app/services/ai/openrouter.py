import httpx

from app.core.config import get_settings
from app.services.ai.base import (
    LegalInfoProvider,
    ProviderError,
    SectionFacts,
    build_prompt,
)


class OpenRouterProvider(LegalInfoProvider):
    """Hosted models via OpenRouter — free-tier models available."""

    name = "openrouter"

    def generate(self, facts: SectionFacts | None, query: str) -> str:
        settings = get_settings()
        if not settings.openrouter_api_key:
            raise ProviderError("OPENROUTER_API_KEY is not configured")
        system, user = build_prompt(facts, query)
        try:
            response = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
                json={
                    "model": settings.openrouter_model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                },
                timeout=settings.ai_timeout_seconds,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError) as exc:
            raise ProviderError(f"OpenRouter request failed: {exc}") from exc
        if not content.strip():
            raise ProviderError("OpenRouter returned an empty response")
        return content.strip()
