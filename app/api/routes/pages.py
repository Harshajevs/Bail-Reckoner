from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "frontend" / "templates")

router = APIRouter(include_in_schema=False)

# Whitelist of served pages; anything else under / is a 404.
PAGES = {
    "about",
    "admin_home",
    "case_judge",
    "drop_judgment",
    "find_advocate",
    "guest",
    "historical_cases",
    "home",
    "judicial_authority",
    "legal_aid_provider",
    "login",
    "prisoner_case_details",
    "register",
    "risk_assignment",
    "take_up",
    "undertrial_prisoner",
}


@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.get("/{page_name}")
def page(request: Request, page_name: str):
    if page_name not in PAGES:
        raise HTTPException(status_code=404, detail="Page not found")
    return templates.TemplateResponse(request, f"{page_name}.html")
