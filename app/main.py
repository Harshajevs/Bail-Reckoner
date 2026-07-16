import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import app.models  # noqa: F401  (register models with Base)
from app.api.routes import auth, cases, legal, pages, providers
from app.core.config import get_settings
from app.db.base import Base
from app.db.seed import seed_legal_sections
from app.db.session import SessionLocal, engine

logging.basicConfig(level=logging.INFO)

BASE_DIR = Path(__file__).resolve().parent.parent
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_legal_sections(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.app_name,
    description="Bail eligibility assessment and legal aid platform for undertrial prisoners",
    lifespan=lifespan,
)

if settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok"}


app.include_router(auth.router, prefix="/api")
app.include_router(cases.router, prefix="/api")
app.include_router(providers.router, prefix="/api")
app.include_router(legal.router, prefix="/api")

app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend" / "static"), name="static")
app.include_router(pages.router)
