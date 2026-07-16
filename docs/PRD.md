# Product Requirements Document — Bail Reckoner Modernization

## 1. Project Overview

Bail Reckoner is a decision-support tool for the Indian criminal justice system.
It helps undertrial prisoners understand their bail eligibility under IPC/BNS
provisions, connects them with nearby legal aid providers, and gives judicial
authorities a workspace to review cases, record opinions, and deliver judgments.

This document defines the requirements for modernizing the existing implementation
**without changing its purpose or core functional behavior**.

## 2. Problem Statement

The current implementation works as a hackathon demo but is not maintainable,
deployable, or safe to operate:

- Four separate app entry points across two frameworks must run together.
- Secrets (a live OpenAI key, DB passwords) are committed to a public repository.
- There is no authentication enforcement; all prisoner PII is publicly readable.
- The frontend is a set of files opened from disk with hardcoded localhost URLs.
- The AI feature depends entirely on a paid OpenAI subscription.
- Dependencies cannot be installed from `requirements.txt` on non-Windows machines.

See `docs/AUDIT.md` for the full audit.

## 3. Current Architecture

Flask (registration) + FastAPI (everything else) + 2 redundant FastAPI apps, two
PostgreSQL databases, duplicated SQLAlchemy models, static HTML frontend calling
`127.0.0.1:5000/:8000` directly. Detailed in the audit.

## 4. Current Limitations

1. Cannot be deployed as a unit (multiple ports, file:// frontend).
2. Cannot be installed reproducibly (broken requirements).
3. Cannot be operated safely (no auth, leaked secrets, PII exposure).
4. Cannot be extended confidently (no tests, duplicated models, dead code).
5. Cannot run without paid OpenAI access.

## 5. Improvement Opportunities

- Consolidate into **one FastAPI service** that serves both the API and the frontend.
- Single database with foreign keys, indexes, and consistent naming.
- Real authentication (JWT) with role claims.
- Environment-driven configuration; zero secrets in code.
- **Provider-agnostic AI layer** with free/local options (Ollama, OpenRouter free
  tier) and a deterministic rule-based fallback that works with no credentials.
- Test suite + reproducible dev setup (SQLite default, Postgres for production).

## 6. Functional Requirements (preserved behavior)

FR1. Users register as prisoner, legal aid provider, or judicial authority.
FR2. Users log in with email + password + role and receive an access token.
FR3. Prisoners look up their case by Aadhaar: charges, bail status, hearing date,
     lawyer, suggestions, judicial opinion.
FR4. Prisoners query bail eligibility for an IPC section and receive section data
     (bailable, BNS mapping, offense type) enriched with AI-generated punishment,
     description, and process guidance.
FR5. Prisoners find nearby legal aid providers filtered by max fee and min
     experience, ranked by distance (Haversine).
FR6. Legal aid providers see unassigned cases and take them up.
FR7. Legal aid providers/judicial authorities view historical judgments by IPC codes.
FR8. Judicial authorities see cases pending opinion, submit opinions and
     suggestions, and record completed cases with judgments.
FR9. Case counts and consolidated case lists per Aadhaar are available.

## 7. Non-Functional Requirements

NFR1. Single command to run the whole stack locally (`uvicorn app.main:app`).
NFR2. No secrets in the repository; configuration via `.env` (documented).
NFR3. All mutating and PII-bearing endpoints require a valid JWT.
NFR4. Works end-to-end with **zero external credentials** (SQLite + rule-based AI).
NFR5. Test suite runs green with `pytest`; CI-friendly (no external services needed).
NFR6. Deployable on a free-tier host (Render/Railway/Fly.io) with Postgres (Neon).
NFR7. Python 3.11+ compatible; all dependencies pinned and installable cross-platform.

## 8. Proposed Architecture

```
Bail-Reckoner/
├── app/
│   ├── main.py                 # single FastAPI app; mounts API + frontend
│   ├── core/
│   │   ├── config.py           # pydantic-settings (.env)
│   │   └── security.py         # bcrypt hashing, JWT create/verify
│   ├── db/
│   │   ├── base.py             # DeclarativeBase
│   │   └── session.py          # engine, SessionLocal, get_db dependency
│   ├── models/                 # users.py, cases.py, legal_sections.py
│   ├── schemas/                # pydantic request/response models
│   ├── services/
│   │   ├── auth.py, cases.py, providers.py
│   │   └── ai/                 # provider abstraction
│   │       ├── base.py         # LegalInfoProvider interface
│   │       ├── ollama.py       # local LLM (free)
│   │       ├── openrouter.py   # hosted free models
│   │       ├── openai.py       # optional paid
│   │       ├── rule_based.py   # deterministic fallback (no credentials)
│   │       └── factory.py      # env-selected with graceful fallback chain
│   └── api/routes/             # auth.py, cases.py, providers.py, legal.py, pages.py
├── frontend/                   # templates/ (Jinja2) + static/ (css, js)
├── data/ipc_sections.csv       # seed knowledge base
├── scripts/seed_db.py
├── tests/
├── docs/                       # AUDIT.md, PRD.md, EXECUTION_PLAN.md
├── requirements.txt            # minimal, pinned
├── .env.example
└── README.md
```

- **One process** serves `/api/*` JSON endpoints and the HTML pages/static assets.
- **One database**; the `legal_sections` knowledge table moves in alongside the
  application tables. Default `sqlite:///./bail_reckoner.db` for development;
  `DATABASE_URL` switches to PostgreSQL for production.
- **AI layer**: `POST /api/legal/bail-info` → factory selects provider from
  `AI_PROVIDER` env (`rule_based` default → `ollama` → `openrouter` → `openai`).
  Every provider implements the same interface; if a remote provider fails, the
  rule-based fallback still answers from the knowledge table. Paid providers are
  plug-in additions, not rewrites.

## 9. Technology Recommendations

| Concern | Choice | Rationale |
|---|---|---|
| Web framework | FastAPI + uvicorn | Already the majority of the code; typed, async, OpenAPI docs |
| ORM | SQLAlchemy 2.0 (typed declarative) | Modern API, works for SQLite + Postgres |
| Validation | Pydantic v2 + pydantic-settings | Schemas + env config |
| Auth | JWT (PyJWT) + bcrypt | Stateless, simple, role claims |
| Templates | Jinja2 via FastAPI | Serve existing HTML with minimal changes |
| AI (default) | Rule-based from knowledge table | Zero cost, deterministic, offline |
| AI (optional) | Ollama / OpenRouter free models / OpenAI | Free-first, swappable |
| Tests | pytest + httpx TestClient | No external services required |

Dropped: Flask, Flask-SQLAlchemy, langchain-postgres/pgvector (initialized but never
used for retrieval — reintroduce only if semantic search becomes a real requirement).

## 10. Migration Strategy

1. Land documentation (audit, PRD, plan) and repo hygiene (`.gitignore`, remove
   artifacts) first.
2. Build the new `app/` package alongside the legacy files; port models with fixes
   (FKs, indexes, `opinion` naming, provider id type bug).
3. Port endpoints route-group by route-group, preserving request/response shapes
   except where broken (documented in the plan).
4. Move the frontend under the app, switch to relative `/api` URLs and served routes.
5. Add tests; verify end-to-end; delete legacy files only after parity is verified.
6. Update README; add deployment guide.

## 11. Risks

| Risk | Mitigation |
|---|---|
| Behavior drift while porting endpoints | Endpoint inventory in audit used as parity checklist; tests per route group |
| Frontend regressions from URL rewrites | Mechanical rewrite + grep sweep for leftover absolute URLs; manual page walk |
| Existing Postgres data not migrated | Schema changes documented; seed script recreates knowledge base; app data was demo data |
| Free AI providers unavailable at runtime | Rule-based fallback always answers |
| Leaked OpenAI key already public | Out of code scope — key must be revoked at provider (flagged to owner) |

## 12. Assumptions

- Existing production data does not need to be preserved (hackathon demo data).
- Aadhaar numbers are demo values; real deployments would need encryption-at-rest
  and masking (documented as future work).
- English-only UI is acceptable (as today).
- The original API consumers are only the bundled frontend pages.

## 13. Execution Roadmap

See `docs/EXECUTION_PLAN.md` for phased execution with scope, risks, and testing
per phase.

## 14. Success Criteria

1. `pip install -r requirements.txt && uvicorn app.main:app` runs the entire product.
2. All functional requirements above work end-to-end via the bundled frontend.
3. No secrets or credentials anywhere in the repository.
4. `pytest` passes with no external services or API keys.
5. Every legacy file is either ported or deliberately deleted with rationale.
6. A new developer can set up the project from the README alone.
