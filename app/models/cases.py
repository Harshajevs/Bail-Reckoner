from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.users import utcnow


class OngoingCase(Base):
    __tablename__ = "ongoing_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prisoner_id: Mapped[int] = mapped_column(ForeignKey("prisoners.id"), index=True)
    aadhar_number: Mapped[str] = mapped_column(String(12), index=True)
    case_number: Mapped[str] = mapped_column(String(50), index=True)
    arrest_conditions: Mapped[str] = mapped_column(Text)
    charges: Mapped[str] = mapped_column(Text)
    offense_date: Mapped[date] = mapped_column(Date)
    arrest_date: Mapped[date] = mapped_column(Date)
    bail_status: Mapped[str] = mapped_column(String(20))
    case_status: Mapped[str] = mapped_column(String(20))
    court_hearing_date: Mapped[date] = mapped_column(Date)
    legal_aid_provider_id: Mapped[int | None] = mapped_column(
        ForeignKey("legal_aid_providers.id"), nullable=True
    )
    case_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    prisoner_lawyer: Mapped[str | None] = mapped_column(String(100), nullable=True)
    suggestions: Mapped[str | None] = mapped_column(Text, nullable=True)
    opinion: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CompletedCase(Base):
    __tablename__ = "completed_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prisoner_id: Mapped[int] = mapped_column(ForeignKey("prisoners.id"), index=True)
    aadhar_number: Mapped[str] = mapped_column(String(12), index=True)
    case_number: Mapped[str] = mapped_column(String(50), index=True)
    arrest_conditions: Mapped[str] = mapped_column(Text)
    charges: Mapped[str] = mapped_column(Text)
    offense_date: Mapped[date] = mapped_column(Date)
    arrest_date: Mapped[date] = mapped_column(Date)
    bail_status: Mapped[str] = mapped_column(String(20))
    case_status: Mapped[str] = mapped_column(String(20))
    court_hearing_date: Mapped[date] = mapped_column(Date)
    judgement: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
