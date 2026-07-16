import logging

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import LegalSection
from app.services.ai.base import ProviderError, SectionFacts
from app.services.ai.factory import get_provider_chain

logger = logging.getLogger(__name__)


def _facts_from_row(row: LegalSection) -> SectionFacts:
    return SectionFacts(
        section=row.section,
        bns_section=row.bns_section,
        offense_type=row.offense_type,
        bailable=row.bailable,
        bail_eligibility=row.bail_eligibility,
        punishment=row.punishment,
        description=row.description,
    )


def get_bail_info(db: Session, section_query: str) -> dict:
    """Look the section up in the knowledge base, then ask the configured AI
    provider chain for guidance. Database facts always lead the response so
    the AI text can never contradict the verified bail status."""
    row = (
        db.query(LegalSection)
        .filter(
            or_(
                LegalSection.section == section_query,
                LegalSection.offense_type.ilike(f"%{section_query}%"),
            )
        )
        .first()
    )
    facts = _facts_from_row(row) if row else None

    content = None
    provider_name = "none"
    for provider in get_provider_chain():
        try:
            content = provider.generate(facts, section_query)
            provider_name = provider.name
            break
        except ProviderError as exc:
            logger.warning("AI provider '%s' failed: %s", provider.name, exc)

    if content is None:
        content = (
            f"No information is available for '{section_query}'. Verify the "
            "section identifier (format: IPC_XXX) or consult a legal aid "
            "provider."
        )

    if facts is not None:
        header = (
            "**Result:**\n"
            f"- IPC Section: {facts.section}\n"
            f"- BNS Section: {facts.bns_section}\n"
            f"- Offense Type: {facts.offense_type}\n"
            f"- Bail Status: {facts.bail_status} (Eligibility: {facts.bail_eligibility})\n\n"
        )
        content = header + content

    return {
        "section": section_query,
        "found_in_database": facts is not None,
        "provider": provider_name,
        "content": content,
    }
