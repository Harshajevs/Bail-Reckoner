from datetime import date

from pydantic import BaseModel, EmailStr, Field

# Accepted spellings of each role (kept from the original frontend forms)
ROLE_ALIASES = {
    "legalaid": "legal_aid",
    "legal_aid": "legal_aid",
    "judicialauthority": "judicial_authority",
    "judicial_authority": "judicial_authority",
    "judicial": "judicial_authority",
    "prisoner": "prisoner",
}


class RegisterRequest(BaseModel):
    role: str
    full_name: str = Field(min_length=1, max_length=100)
    dob: date
    aadhar_number: str = Field(min_length=12, max_length=12, pattern=r"^\d{12}$")
    gender: str
    email: EmailStr
    password: str = Field(min_length=6)
    address: str

    # Legal aid provider / judicial authority fields
    designation: str | None = None
    license_number: str | None = None
    experience: int | None = None
    contact_number: str | None = None
    working_location: str | None = None  # "latitude,longitude"
    legal_fee: float | None = None
    languages_known: str | None = None

    # Prisoner fields
    phone_number: str | None = None
    occupation: str | None = None
    father_name: str | None = None
    father_aadhar: str | None = None
    mother_name: str | None = None
    mother_aadhar: str | None = None
    siblings_name: str | None = None
    siblings_aadhar: str | None = None
    family_member_designation: str | None = None
    case_history: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: str


class LoginResponse(BaseModel):
    message: str
    name: str
    role: str
    access_token: str
    token_type: str = "bearer"
