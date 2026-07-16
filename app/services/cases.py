from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import CompletedCase, LegalAidProvider, OngoingCase, Prisoner
from app.schemas.cases import (
    CompletedCaseCreate,
    HistoricalCasesRequest,
    OngoingCaseCreate,
    TakeUpCaseRequest,
)


def add_ongoing_case(db: Session, data: OngoingCaseCreate) -> OngoingCase:
    case = OngoingCase(**data.model_dump())
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def add_completed_case(db: Session, data: CompletedCaseCreate) -> CompletedCase:
    case = CompletedCase(**data.model_dump())
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def list_ongoing_cases(db: Session, limit: int, offset: int) -> list[OngoingCase]:
    return db.query(OngoingCase).order_by(OngoingCase.id).limit(limit).offset(offset).all()


def list_completed_cases(db: Session, limit: int, offset: int) -> list[CompletedCase]:
    return (
        db.query(CompletedCase).order_by(CompletedCase.id).limit(limit).offset(offset).all()
    )


def lookup_case_by_aadhar(db: Session, aadhar_number: str) -> OngoingCase:
    prisoner = db.query(Prisoner).filter_by(aadhar_number=aadhar_number).first()
    if not prisoner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aadhar number doesn't match the prisoner record.",
        )
    case = db.query(OngoingCase).filter_by(aadhar_number=aadhar_number).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending cases found for this Aadhar number.",
        )
    return case


def count_ongoing_cases(db: Session, aadhar_number: str) -> int:
    return db.query(OngoingCase).filter_by(aadhar_number=aadhar_number).count()


def count_completed_cases(db: Session, aadhar_number: str) -> int:
    return db.query(CompletedCase).filter_by(aadhar_number=aadhar_number).count()


def all_cases_by_aadhar(db: Session, aadhar_number: str) -> dict:
    ongoing = db.query(OngoingCase).filter_by(aadhar_number=aadhar_number).all()
    completed = db.query(CompletedCase).filter_by(aadhar_number=aadhar_number).all()
    return {"ongoing_cases": ongoing, "completed_cases": completed}


def pending_cases(db: Session) -> list[OngoingCase]:
    """Cases not yet taken up by a legal aid provider."""
    return (
        db.query(OngoingCase)
        .filter(OngoingCase.legal_aid_provider_id.is_(None))
        .order_by(OngoingCase.id)
        .all()
    )


def pending_opinions(db: Session) -> list[OngoingCase]:
    """Cases awaiting a judicial opinion."""
    return (
        db.query(OngoingCase)
        .filter(OngoingCase.opinion.is_(None))
        .order_by(OngoingCase.id)
        .all()
    )


def _get_case_or_404(db: Session, case_id: int) -> OngoingCase:
    case = db.query(OngoingCase).filter_by(id=case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )
    return case


def submit_opinion(db: Session, case_id: int, opinion: str) -> None:
    case = _get_case_or_404(db, case_id)
    case.opinion = opinion
    db.commit()


def submit_suggestion(db: Session, case_id: int, suggestion: str) -> None:
    case = _get_case_or_404(db, case_id)
    case.suggestions = suggestion
    db.commit()


def take_up_case(db: Session, case_id: int, data: TakeUpCaseRequest) -> None:
    provider = (
        db.query(LegalAidProvider)
        .filter_by(license_number=data.license_number)
        .first()
    )
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Legal Aid Provider not found"
        )
    case = _get_case_or_404(db, case_id)
    case.legal_aid_provider_id = provider.id
    case.prisoner_lawyer = data.prisoner_lawyer
    db.commit()


def historical_cases(db: Session, data: HistoricalCasesRequest) -> list[CompletedCase]:
    return (
        db.query(CompletedCase)
        .filter(or_(*[CompletedCase.charges.ilike(f"%{ipc}%") for ipc in data.ipcs]))
        .all()
    )


def bail_status_by_prisoner_id(db: Session, prisoner_id: int) -> str:
    case = db.query(OngoingCase).filter_by(prisoner_id=prisoner_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No ongoing case found for Prisoner ID: {prisoner_id}",
        )
    return case.bail_status
