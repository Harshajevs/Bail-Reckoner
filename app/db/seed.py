import csv
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import LegalSection

logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "ipc_sections.csv"


def seed_legal_sections(db: Session, csv_path: Path = DATA_FILE) -> int:
    """Load the IPC knowledge base from CSV. Idempotent: existing sections
    are left untouched. Returns the number of rows inserted."""
    if not csv_path.exists():
        logger.warning("Seed file not found: %s", csv_path)
        return 0

    existing = {row.section for row in db.query(LegalSection.section).all()}
    inserted = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["section"] in existing:
                continue
            db.add(
                LegalSection(
                    section=row["section"],
                    bns_section=row["bns_section"] or None,
                    offense_type=row["offense_type"],
                    bailable=row["bailable"].strip().lower() == "true",
                    bail_eligibility=row["bail_eligibility"],
                    punishment=row["punishment"] or None,
                    description=row["description"] or None,
                )
            )
            inserted += 1

    db.commit()
    if inserted:
        logger.info("Seeded %d legal sections", inserted)
    return inserted
