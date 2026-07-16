from app.services.ai.base import LegalInfoProvider, ProviderError, SectionFacts


class RuleBasedProvider(LegalInfoProvider):
    """Deterministic provider that answers purely from the knowledge base.

    Needs no credentials or network access, so it is the default and the
    final fallback for every other provider.
    """

    name = "rule_based"

    def generate(self, facts: SectionFacts | None, query: str) -> str:
        if facts is None:
            raise ProviderError(
                f"No knowledge base entry for '{query}' and no LLM provider "
                "is configured to generate an answer."
            )

        lines = [
            f"- Punishment: {facts.punishment or 'Refer to the bare act for the prescribed punishment.'}",
            f"- Description: {facts.description or facts.offense_type}",
            "- Process to Follow: "
            + (
                "This offense is bailable. Apply for bail before the police "
                "station officer-in-charge or the magistrate under Section 436 "
                "CrPC (Section 478 BNSS). Bail is a matter of right; furnish "
                "the bail bond with sureties as directed."
                if facts.bailable
                else "This offense is non-bailable. File a bail application "
                "before the Sessions Court or High Court under Section 437/439 "
                "CrPC (Sections 480/483 BNSS). Bail is at the court's "
                "discretion; engage a legal aid provider to argue factors such "
                "as period of custody already served, evidence tampering risk, "
                "and flight risk."
            ),
        ]
        return "\n".join(lines)
