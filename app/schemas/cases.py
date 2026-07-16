from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class OngoingCaseCreate(BaseModel):
    prisoner_id: int
    aadhar_number: str = Field(min_length=12, max_length=12, pattern=r"^\d{12}$")
    case_number: str
    arrest_conditions: str
    charges: str
    offense_date: date
    arrest_date: date
    bail_status: str
    case_status: str
    court_hearing_date: date
    legal_aid_provider_id: int | None = None
    case_summary: str | None = None
    evidence_details: str | None = None


class CompletedCaseCreate(BaseModel):
    prisoner_id: int
    aadhar_number: str = Field(min_length=12, max_length=12, pattern=r"^\d{12}$")
    case_number: str
    arrest_conditions: str
    charges: str
    offense_date: date
    arrest_date: date
    bail_status: str
    case_status: str
    court_hearing_date: date
    judgement: str


class OngoingCaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    prisoner_id: int
    aadhar_number: str
    case_number: str
    arrest_conditions: str
    charges: str
    offense_date: date
    arrest_date: date
    bail_status: str
    case_status: str
    court_hearing_date: date
    legal_aid_provider_id: int | None = None
    case_summary: str | None = None
    evidence_details: str | None = None
    prisoner_lawyer: str | None = None
    suggestions: str | None = None
    opinion: str | None = None
    created_at: datetime | None = None


class CompletedCaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    prisoner_id: int
    aadhar_number: str
    case_number: str
    arrest_conditions: str
    charges: str
    offense_date: date
    arrest_date: date
    bail_status: str
    case_status: str
    court_hearing_date: date
    judgement: str
    created_at: datetime | None = None


class CaseLookupOut(BaseModel):
    """Prisoner-facing case summary returned by Aadhaar validation."""

    case_number: str
    charges: str
    bail_status: str
    court_hearing_date: date
    case_summary: str | None = None
    suggestions: str | None = None
    opinion: str | None = None
    legal_aid_provider_id: int | None = None
    prisoner_lawyer: str | None = None


class OpinionRequest(BaseModel):
    opinion: str


class SuggestionRequest(BaseModel):
    suggestion: str


class TakeUpCaseRequest(BaseModel):
    prisoner_lawyer: str
    license_number: str


class HistoricalCasesRequest(BaseModel):
    ipcs: list[str] = Field(min_length=1)


class MessageResponse(BaseModel):
    message: str
