from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.cases import (
    CaseLookupOut,
    CompletedCaseCreate,
    CompletedCaseOut,
    HistoricalCasesRequest,
    MessageResponse,
    OngoingCaseCreate,
    OngoingCaseOut,
    OpinionRequest,
    SuggestionRequest,
    TakeUpCaseRequest,
)
from app.services import cases as case_service

router = APIRouter(tags=["cases"], dependencies=[Depends(get_current_user)])


@router.post("/add-ongoing-case", response_model=MessageResponse, status_code=201)
def add_ongoing_case(data: OngoingCaseCreate, db: Session = Depends(get_db)):
    case_service.add_ongoing_case(db, data)
    return {"message": "Ongoing case added successfully"}


@router.post("/add-completed-case", response_model=MessageResponse, status_code=201)
def add_completed_case(data: CompletedCaseCreate, db: Session = Depends(get_db)):
    case_service.add_completed_case(db, data)
    return {"message": "Completed case added successfully"}


@router.get("/ongoing-cases", response_model=list[OngoingCaseOut])
def list_ongoing_cases(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return case_service.list_ongoing_cases(db, limit, offset)


@router.get("/completed-cases", response_model=list[CompletedCaseOut])
def list_completed_cases(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return case_service.list_completed_cases(db, limit, offset)


@router.get("/validate-aadhar/{aadhar_number}", response_model=CaseLookupOut)
def validate_aadhar(aadhar_number: str, db: Session = Depends(get_db)):
    case = case_service.lookup_case_by_aadhar(db, aadhar_number)
    return CaseLookupOut(
        case_number=case.case_number,
        charges=case.charges,
        bail_status=case.bail_status,
        court_hearing_date=case.court_hearing_date,
        case_summary=case.case_summary,
        suggestions=case.suggestions,
        opinion=case.opinion,
        legal_aid_provider_id=case.legal_aid_provider_id,
        prisoner_lawyer=case.prisoner_lawyer,
    )


@router.get("/ongoing-cases/{aadhar_number}")
def count_ongoing(aadhar_number: str, db: Session = Depends(get_db)):
    return {"count": case_service.count_ongoing_cases(db, aadhar_number)}


@router.get("/completed-cases/{aadhar_number}")
def count_completed(aadhar_number: str, db: Session = Depends(get_db)):
    return {"count": case_service.count_completed_cases(db, aadhar_number)}


@router.get("/all-cases/{aadhar_number}")
def all_cases(aadhar_number: str, db: Session = Depends(get_db)):
    result = case_service.all_cases_by_aadhar(db, aadhar_number)
    return {
        "ongoing_cases": [
            OngoingCaseOut.model_validate(c) for c in result["ongoing_cases"]
        ],
        "completed_cases": [
            CompletedCaseOut.model_validate(c) for c in result["completed_cases"]
        ],
    }


@router.get("/pending-cases", response_model=list[OngoingCaseOut])
def pending_cases(db: Session = Depends(get_db)):
    return case_service.pending_cases(db)


@router.get("/pending-opinions", response_model=list[OngoingCaseOut])
def pending_opinions(db: Session = Depends(get_db)):
    return case_service.pending_opinions(db)


@router.post("/submit-opinion/{case_id}", response_model=MessageResponse)
def submit_opinion(
    case_id: int, data: OpinionRequest, db: Session = Depends(get_db)
):
    case_service.submit_opinion(db, case_id, data.opinion)
    return {"message": "Opinion submitted successfully"}


@router.post("/suggestion/{case_id}", response_model=MessageResponse)
def submit_suggestion(
    case_id: int, data: SuggestionRequest, db: Session = Depends(get_db)
):
    case_service.submit_suggestion(db, case_id, data.suggestion)
    return {"message": "Suggestion added or updated successfully"}


@router.post("/take-up-case/{case_id}", response_model=MessageResponse)
def take_up_case(
    case_id: int, data: TakeUpCaseRequest, db: Session = Depends(get_db)
):
    case_service.take_up_case(db, case_id, data)
    return {"message": "Case taken up successfully by Legal Aid Provider"}


@router.post("/historical-cases")
def historical_cases(data: HistoricalCasesRequest, db: Session = Depends(get_db)):
    cases = case_service.historical_cases(db, data)
    if not cases:
        return {"message": "No historical cases found for the provided IPCs."}
    return {
        "matching_cases": [
            {
                "case_number": c.case_number,
                "prisoner_id": c.prisoner_id,
                "aadhar_number": c.aadhar_number,
                "charges": c.charges,
                "judgement": c.judgement,
                "court_hearing_date": c.court_hearing_date,
            }
            for c in cases
        ]
    }


@router.get("/bail-status/{prisoner_id}")
def bail_status(prisoner_id: int, db: Session = Depends(get_db)):
    return {"bail_status": case_service.bail_status_by_prisoner_id(db, prisoner_id)}
