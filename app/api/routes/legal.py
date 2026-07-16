from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.legal import BailInfoRequest, BailInfoResponse
from app.services.legal_info import get_bail_info

# Public: the guest page offers bail-eligibility lookup before login
router = APIRouter(tags=["legal"])


@router.post("/get-bail-status", response_model=BailInfoResponse)
def bail_info(data: BailInfoRequest, db: Session = Depends(get_db)):
    section = data.charges.strip().upper()
    if not section.startswith("IPC_"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid IPC section format. Must be IPC_XXX.",
        )
    return get_bail_info(db, section)
