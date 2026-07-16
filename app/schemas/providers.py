from pydantic import BaseModel, Field


class NearestProvidersRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    maxAdvocateFee: float | None = None
    minExperience: int = 0


class ProviderOut(BaseModel):
    name: str
    designation: str
    email: str
    contact_number: str
    fee: float
    experience: int
    languages_known: str | None = None
    distance: float


class ProviderLocationOut(BaseModel):
    latitude: float
    longitude: float
