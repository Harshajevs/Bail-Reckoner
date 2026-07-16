import logging

from app.core.config import get_settings
from app.services.ai.base import LegalInfoProvider
from app.services.ai.ollama import OllamaProvider
from app.services.ai.openai_provider import OpenAIProvider
from app.services.ai.openrouter import OpenRouterProvider
from app.services.ai.rule_based import RuleBasedProvider

logger = logging.getLogger(__name__)

PROVIDERS: dict[str, type[LegalInfoProvider]] = {
    "rule_based": RuleBasedProvider,
    "ollama": OllamaProvider,
    "openrouter": OpenRouterProvider,
    "openai": OpenAIProvider,
}


def get_provider_chain() -> list[LegalInfoProvider]:
    """Providers to try in order. The configured provider comes first;
    rule_based is always appended as the no-credential fallback."""
    settings = get_settings()
    selected = settings.ai_provider.strip().lower()
    if selected not in PROVIDERS:
        logger.warning("Unknown AI_PROVIDER '%s'; using rule_based", selected)
        selected = "rule_based"

    chain: list[LegalInfoProvider] = [PROVIDERS[selected]()]
    if selected != "rule_based":
        chain.append(RuleBasedProvider())
    return chain
