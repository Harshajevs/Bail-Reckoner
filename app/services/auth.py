from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models import JudicialAuthority, LegalAidProvider, Prisoner
from app.schemas.auth import ROLE_ALIASES, LoginRequest, RegisterRequest

ROLE_MODELS = {
    "legal_aid": LegalAidProvider,
    "judicial_authority": JudicialAuthority,
    "prisoner": Prisoner,
}


def normalize_role(role: str) -> str:
    normalized = ROLE_ALIASES.get(role.strip().lower())
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid role: {role}. Must be 'legal_aid', "
                "'judicial_authority', or 'prisoner'"
            ),
        )
    return normalized


def _require(data: RegisterRequest, fields: list[str]) -> None:
    missing = [f for f in fields if getattr(data, f) in (None, "")]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required fields: {', '.join(missing)}",
        )


def _parse_working_location(value: str) -> str:
    try:
        latitude, longitude = map(float, value.split(","))
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ValueError
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid working location format. Expected 'latitude,longitude'.",
        )
    return f"{latitude},{longitude}"


def register_user(db: Session, data: RegisterRequest) -> str:
    role = normalize_role(data.role)
    model = ROLE_MODELS[role]

    if db.query(model).filter_by(email=data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    password_hash = hash_password(data.password)

    if role == "legal_aid":
        _require(
            data,
            ["designation", "license_number", "experience", "contact_number",
             "working_location", "legal_fee"],
        )
        user = LegalAidProvider(
            full_name=data.full_name,
            dob=data.dob,
            aadhar_number=data.aadhar_number,
            designation=data.designation,
            license_number=data.license_number,
            address=data.address,
            experience=data.experience,
            contact_number=data.contact_number,
            email=data.email,
            gender=data.gender,
            working_location=_parse_working_location(data.working_location),
            legal_fee=data.legal_fee,
            languages_known=data.languages_known,
            password_hash=password_hash,
        )
    elif role == "judicial_authority":
        _require(
            data, ["designation", "license_number", "experience", "contact_number"]
        )
        user = JudicialAuthority(
            full_name=data.full_name,
            dob=data.dob,
            address=data.address,
            aadhar_number=data.aadhar_number,
            contact_number=data.contact_number,
            email=data.email,
            gender=data.gender,
            designation=data.designation,
            license_number=data.license_number,
            experience=data.experience,
            password_hash=password_hash,
        )
    else:
        _require(
            data,
            ["phone_number", "occupation", "father_name", "father_aadhar",
             "mother_name", "mother_aadhar"],
        )
        user = Prisoner(
            full_name=data.full_name,
            dob=data.dob,
            aadhar_number=data.aadhar_number,
            gender=data.gender,
            phone_number=data.phone_number,
            email=data.email,
            occupation=data.occupation,
            address=data.address,
            father_name=data.father_name,
            father_aadhar=data.father_aadhar,
            mother_name=data.mother_name,
            mother_aadhar=data.mother_aadhar,
            siblings_name=data.siblings_name,
            siblings_aadhar=data.siblings_aadhar,
            family_member_designation=data.family_member_designation,
            case_history=data.case_history,
            password_hash=password_hash,
        )

    db.add(user)
    db.commit()
    return role


def login_user(db: Session, data: LoginRequest) -> dict:
    role = normalize_role(data.role)
    model = ROLE_MODELS[role]

    user = db.query(model).filter_by(email=data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(subject=user.email, role=role, name=user.full_name)
    return {
        "message": "Login successful",
        "name": user.full_name,
        "role": role,
        "access_token": token,
    }
