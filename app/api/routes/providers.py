from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.providers import (
    NearestProvidersRequest,
    ProviderLocationOut,
    ProviderOut,
)
from app.services import providers as provider_service

# Public: the guest "find an advocate" page uses these before login
router = APIRouter(tags=["providers"])


@router.post("/get-nearest-providers", response_model=list[ProviderOut])
def get_nearest_providers(
    data: NearestProvidersRequest, db: Session = Depends(get_db)
):
    return provider_service.nearest_providers(db, data)


@router.get("/get-provider-location/{provider_id}", response_model=ProviderLocationOut)
def get_provider_location(provider_id: int, db: Session = Depends(get_db)):
    return provider_service.provider_location(db, provider_id)
