from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class LegalAidProvider(Base):
    __tablename__ = "legal_aid_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    dob: Mapped[date] = mapped_column(Date)
    aadhar_number: Mapped[str] = mapped_column(String(12), index=True)
    designation: Mapped[str] = mapped_column(String(100))
    license_number: Mapped[str] = mapped_column(String(50), unique=True)
    address: Mapped[str] = mapped_column(Text)
    experience: Mapped[int] = mapped_column(Integer)
    contact_number: Mapped[str] = mapped_column(String(15))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    gender: Mapped[str] = mapped_column(String(10))
    # "latitude,longitude" — parsed for distance ranking
    working_location: Mapped[str] = mapped_column(Text)
    legal_fee: Mapped[float] = mapped_column(Float)
    languages_known: Mapped[str | None] = mapped_column(Text, nullable=True)
    password_hash: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class JudicialAuthority(Base):
    __tablename__ = "judicial_authorities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    dob: Mapped[date] = mapped_column(Date)
    address: Mapped[str] = mapped_column(Text)
    aadhar_number: Mapped[str] = mapped_column(String(12), index=True)
    contact_number: Mapped[str] = mapped_column(String(15))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    gender: Mapped[str] = mapped_column(String(10))
    designation: Mapped[str] = mapped_column(String(100))
    license_number: Mapped[str] = mapped_column(String(50))
    experience: Mapped[int] = mapped_column(Integer)
    password_hash: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Prisoner(Base):
    __tablename__ = "prisoners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    dob: Mapped[date] = mapped_column(Date)
    aadhar_number: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    gender: Mapped[str] = mapped_column(String(10))
    phone_number: Mapped[str] = mapped_column(String(15))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    occupation: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(Text)
    father_name: Mapped[str] = mapped_column(String(100))
    father_aadhar: Mapped[str] = mapped_column(String(12))
    mother_name: Mapped[str] = mapped_column(String(100))
    mother_aadhar: Mapped[str] = mapped_column(String(12))
    siblings_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    siblings_aadhar: Mapped[str | None] = mapped_column(String(12), nullable=True)
    family_member_designation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    case_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    password_hash: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
