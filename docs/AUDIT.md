# Repository Audit — Bail Reckoner

Audit of the codebase as it existed before modernization (commit `eced201`).

## 1. Project Overview

Bail Reckoner is a Smart India Hackathon project (Dec 2024 – Jan 2025) that assesses
bail eligibility for undertrial prisoners using legal provisions from the IPC/BNS,
supports case lookup via Aadhaar, connects prisoners with nearby legal aid providers,
and lets judicial authorities record opinions and judgments.

Three user roles exist: **Undertrial Prisoner**, **Legal Aid Provider**, and
**Judicial Authority**.

## 2. Architecture (as found)

```
Browser (static HTML files, opened directly from disk)
   ├── fetch → http://127.0.0.1:5000  Flask app        (app.py)
   └── fetch → http://127.0.0.1:8000  FastAPI app      (main.py)
                                       ├── query3.py    (OpenAI GPT-4 enrichment)
                                       └── PostgreSQL   (2 separate databases)
Redundant, unwired services:
   ├── ongoing.py       (second FastAPI app duplicating case endpoints)
   └── backend_code.py  (third FastAPI app duplicating /get-bail-status)
```

- **Two parallel backends.** Registration and two case endpoints live in a Flask app
  (`app.py`); login and everything else live in a FastAPI app (`main.py`). Both must
  run simultaneously on different ports for the product to work.
- **Model duplication.** The same five tables are declared twice — once with
  Flask-SQLAlchemy in `models.py`, once with plain SQLAlchemy in `main.py` — with
  subtle divergences (e.g. `working_location` is `Text` in one and `String(50)` in
  the other; `OngoingCase.aadhar_number` is required in one declaration and absent
  from the Flask insert path).
- **Two databases.** Application data in `bail_reckoner`, the IPC knowledge base in
  `_langchain1` (and a third name, `bail_reckoner_langchain`, in dead code).
- **Frontend never served.** Only `index.html` is rendered by Flask; every other page
  navigates via `window.location.href='home.html'`, which only works when the files
  are opened from disk. CSS files sit in `templates/` alongside HTML.

## 3. Tech Stack (as found)

| Layer      | Technology |
|------------|------------|
| Backends   | Flask 3.1 + FastAPI (version unpinned, not in requirements.txt) |
| ORM        | Flask-SQLAlchemy 3.1 and raw SQLAlchemy 2.0 (duplicated) |
| Database   | PostgreSQL (×2), pgvector via langchain-postgres (initialized, never queried) |
| AI         | OpenAI GPT-4 via `openai` + `langchain_openai` (hardcoded key) |
| Frontend   | Hand-written HTML/CSS/vanilla JS, Font Awesome CDN |
| Auth       | bcrypt password hashing; no sessions, tokens, or route protection |

## 4. Endpoint Inventory

| Endpoint | App | Purpose |
|---|---|---|
| `POST /register` | Flask | Register any of the 3 roles |
| `POST /undertrial_prisoner` | Flask | Add ongoing case (duplicate of below) |
| `GET /bail_status/<prisoner_id>` | Flask | Bail status by prisoner id |
| `POST /add-completed-case` | Flask **and** FastAPI | Duplicate implementations |
| `POST /login` | FastAPI | Role-based login (returns name only) |
| `POST /add-ongoing-case` | FastAPI | Add ongoing case |
| `GET /validate-aadhar/{aadhar}` | FastAPI | Prisoner case lookup by Aadhaar |
| `GET /ongoing-cases`, `/completed-cases` | FastAPI | List all (unauthenticated) |
| `GET /ongoing-cases/{aadhar}`, `/completed-cases/{aadhar}` | FastAPI | Counts |
| `GET /all-cases/{aadhar}` | FastAPI | Serializes raw ORM `__dict__` |
| `GET /pending-cases`, `/pending-opinions` | FastAPI | Judicial/legal-aid queues |
| `POST /submit-opinion/{id}`, `/take-up-case/{id}` | FastAPI | Case updates |
| `POST /historical-cases` | FastAPI | ILIKE search of judgments by IPC |
| `POST /get-bail-status` | FastAPI | IPC lookup + GPT-4 enrichment |
| `POST /get-nearest-providers`, `GET /get-provider-location/{id}` | FastAPI | Haversine advocate discovery |

`ongoing.py` and `backend_code.py` re-declare six of these endpoints in separate,
unlaunched FastAPI apps.

## 5. Security Findings (critical first)

1. **Live OpenAI API key committed** in `query3.py` and `database.py`. The repository
   is public — the key must be treated as compromised and revoked.
2. **Database passwords hardcoded** in 4 files (`app.py`, `main.py`, `query3.py`,
   `database.py`, `database_setup.py`).
3. **No authentication enforcement.** Login verifies a password but issues no
   session/token; every data endpoint (including full dumps of all prisoners' cases
   and Aadhaar numbers) is publicly callable.
4. **CORS `allow_origins=["*"]` with `allow_credentials=True`** — an invalid and
   unsafe combination.
5. **Sensitive PII** (Aadhaar numbers of prisoners and their family members) stored
   and returned without masking, and exposed via unauthenticated list endpoints.
6. **Raw exception messages returned to clients** (`detail=f"Database error: {e}"`),
   leaking schema/internal details.
7. Flask runs with `debug=True` (Werkzeug debugger allows RCE if exposed).

## 6. Bugs & Correctness Issues

- `take-up-case` writes a **string license number into `legal_aid_provider_id`
  (Integer column)** — fails on Postgres, silently corrupts intent.
- Flask's `/undertrial_prisoner` inserts an `OngoingCase` **without
  `aadhar_number`**, which is `NOT NULL` — the endpoint can never succeed against
  the schema created by `main.py`.
- `GET /completed-cases` uses `Depends(get_session)` on a **context-manager
  generator**, which FastAPI cannot inject correctly; same bug in `ongoing.py`.
- `get_ongoing_cases` defined twice in `main.py` (route shadowing risk),
  `Base.metadata.create_all` called twice.
- `models.py` column named `Opinion` (capitalized) — inconsistent and error-prone.
- No FK constraints anywhere (`prisoner_id`, `legal_aid_provider_id` are bare ints).
- Dates handled as strings and parsed ad hoc per endpoint.

## 7. Dependency & Tooling Issues

- `requirements.txt` is a **Jupyter environment dump**: notebook, matplotlib, seaborn,
  `pywin32` (Windows-only — breaks install on macOS/Linux)… while **fastapi, uvicorn,
  flask-cors, openai, langchain-postgres are missing** even though the code imports them.
- `datetime.utcnow` (deprecated since Python 3.12) used as column default.
- `Query.get()` (legacy SQLAlchemy API) used.
- `__pycache__/` with `.pyc` files committed; no `.gitignore`.
- Dead artifacts: empty `pgvector/` dir, empty `approve.html`, `users.html`,
  `ongoing_cases.html`, duplicate `about1.html`, unused `database_setup.py`.
- README is a single line. No tests, no CI, no migrations, no env management.

## 8. AI Integration (as found)

- `query3.py` looks up an IPC section in the `bail_cases` table with plain SQL, then
  calls **GPT-4** to generate punishment/description/process text; if no DB row, GPT-4
  generates everything.
- A PGVector store and OpenAI embeddings are initialized at import time (blocking,
  requires network) **but never used for retrieval** — the vector store is dead weight.
- `database.py` is a one-off CSV ingestion script with a hardcoded local Windows/Linux
  path, embedding every row and storing the vector as JSON text in a column that is
  never read.
- Fully dependent on a paid OpenAI key; no provider abstraction, no fallback, no
  offline mode.

## 9. Scalability & Performance

- Module-level global DB session in `query3.py` (shared, never refreshed, thread-unsafe).
- Nearest-provider search loads **all** providers and computes Haversine in Python —
  acceptable at hackathon scale, unindexed beyond that.
- `historical-cases` uses unanchored `ILIKE '%…%'` across all judgments.
- No pagination on any list endpoint.

## 10. Technical Debt Summary

| Category | Debt |
|---|---|
| Architecture | 4 app entry points, 2 databases, duplicated models/endpoints |
| Security | Committed secrets, no authz, PII exposure, permissive CORS |
| Data | No FKs, no indexes, type-mismatch writes, string dates |
| Code quality | Dead files, duplicate code, inconsistent naming, no structure |
| Operations | Un-installable requirements, no env config, no tests, no docs |
| AI | Hardcoded paid provider, unused vector store, no abstraction |
