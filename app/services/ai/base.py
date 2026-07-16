from abc import ABC, abstractmethod


class SectionFacts:
    """Verified facts about a legal section, loaded from the knowledge base."""

    def __init__(
        self,
        section: str,
        bns_section: str | None,
        offense_type: str,
        bailable: bool,
        bail_eligibility: str,
        punishment: str | None = None,
        description: str | None = None,
    ):
        self.section = section
        self.bns_section = bns_section or "Not Applicable"
        self.offense_type = offense_type
        self.bailable = bailable
        self.bail_eligibility = bail_eligibility
        self.punishment = punishment
        self.description = description

    @property
    def bail_status(self) -> str:
        return "Yes" if self.bailable else "No"


class ProviderError(Exception):
    """Raised by a provider when it cannot produce an answer."""


class LegalInfoProvider(ABC):
    """Interface every AI backend implements.

    Adding a new provider (paid or free) means implementing this class and
    registering it in the factory — no changes anywhere else.
    """

    name: str = "base"

    @abstractmethod
    def generate(self, facts: SectionFacts | None, query: str) -> str:
        """Return legal guidance text for a section.

        `facts` holds database-verified data when the section is known;
        None means the provider must answer from the query alone.
        Raises ProviderError when the backend is unavailable or fails.
        """


def build_prompt(facts: SectionFacts | None, query: str) -> tuple[str, str]:
    """Shared prompt construction for LLM-backed providers."""
    system = (
        "You are a legal expert on Indian criminal law (IPC, BNS, CrPC). "
        "Provide accurate, concise guidance for undertrial prisoners and "
        "legal aid providers."
    )
    if facts is not None:
        user = f"""Provide detailed legal information for:

Section: {facts.section}
Offense Type: {facts.offense_type}
Bail Status: {facts.bail_status} (Eligibility: {facts.bail_eligibility})

Format:
- Punishment:
- Description:
- Process to Follow:"""
    else:
        user = f"""Provide detailed legal information for:

Query: {query}

Format:
- IPC Section:
- Offense Type:
- Bail Status:
- Punishment:
- Description:
- Process to Follow:"""
    return system, user
