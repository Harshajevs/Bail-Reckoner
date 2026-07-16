from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest
from app.schemas.cases import MessageResponse
from app.services import auth as auth_service

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=MessageResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    auth_service.register_user(db, data)
    return {"message": "Registration successful"}


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login_user(db, data)
