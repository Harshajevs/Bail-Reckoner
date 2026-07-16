from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LegalSection(Base):
    """Knowledge base of IPC sections with BNS mapping and bail information.

    Seeded from data/ipc_sections.csv; the deterministic (rule-based) AI
    provider answers directly from this table.
    """

    __tablename__ = "legal_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section: Mapped[str] = mapped_column(String(20), unique=True, index=True)  # e.g. IPC_302
    bns_section: Mapped[str | None] = mapped_column(String(20), nullable=True)
    offense_type: Mapped[str] = mapped_column(String(200))
    bailable: Mapped[bool] = mapped_column(Boolean)
    bail_eligibility: Mapped[str] = mapped_column(Text)
    punishment: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
