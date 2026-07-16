from pydantic import BaseModel


class BailInfoRequest(BaseModel):
    charges: str  # e.g. "IPC_302"


class BailInfoResponse(BaseModel):
    section: str
    found_in_database: bool
    provider: str
    content: str
