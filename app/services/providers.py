import logging
from math import atan2, cos, radians, sin, sqrt

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import LegalAidProvider
from app.schemas.providers import NearestProvidersRequest

logger = logging.getLogger(__name__)

EARTH_RADIUS_KM = 6371


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return EARTH_RADIUS_KM * 2 * atan2(sqrt(a), sqrt(1 - a))


def _parse_location(value: str | None) -> tuple[float, float] | None:
    if not value or "," not in value:
        return None
    try:
        lat, lon = map(float, value.split(","))
        return lat, lon
    except ValueError:
        return None


def nearest_providers(db: Session, data: NearestProvidersRequest) -> list[dict]:
    max_fee = data.maxAdvocateFee if data.maxAdvocateFee is not None else float("inf")

    providers = (
        db.query(LegalAidProvider)
        .filter(
            LegalAidProvider.legal_fee <= max_fee,
            LegalAidProvider.experience >= data.minExperience,
        )
        .all()
    )

    results = []
    for provider in providers:
        location = _parse_location(provider.working_location)
        if location is None:
            logger.warning(
                "Skipping provider %s: invalid working_location", provider.id
            )
            continue
        distance = haversine_km(data.latitude, data.longitude, *location)
        results.append(
            {
                "name": provider.full_name,
                "designation": provider.designation,
                "email": provider.email,
                "contact_number": provider.contact_number,
                "fee": provider.legal_fee,
                "experience": provider.experience,
                "languages_known": provider.languages_known,
                "distance": round(distance, 2),
            }
        )

    results.sort(key=lambda p: p["distance"])
    return results


def provider_location(db: Session, provider_id: int) -> dict:
    provider = db.query(LegalAidProvider).filter_by(id=provider_id).first()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found"
        )
    location = _parse_location(provider.working_location)
    if location is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid working_location format",
        )
    return {"latitude": location[0], "longitude": location[1]}
