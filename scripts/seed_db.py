"""Create all tables and seed the legal-section knowledge base.

Usage: python -m scripts.seed_db
"""

from app.db.base import Base
from app.db.seed import seed_legal_sections
from app.db.session import SessionLocal, engine
import app.models  # noqa: F401  (register models with Base)


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        inserted = seed_legal_sections(db)
        print(f"Tables created. Seeded {inserted} legal sections.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
