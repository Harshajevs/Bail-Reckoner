# Bail Reckoner

An AI-assisted decision-support platform for the Indian criminal justice system.
It helps **undertrial prisoners** understand their bail eligibility under
IPC/BNS provisions, connects them with nearby **legal aid providers**, and gives
**judicial authorities** a workspace to review cases, record opinions, and
deliver judgments.

Originally built for Smart India Hackathon (Dec 2024 – Jan 2025); since
modernized into a single, production-style FastAPI application. The audit of the
original implementation, the modernization PRD, and the phased execution plan
live in [`docs/`](docs/).

## Features

- **Role-based accounts** — prisoner, legal aid provider, judicial authority —
  with bcrypt-hashed passwords and JWT login.
- **Bail eligibility lookup** — query an IPC section (e.g. `IPC_302`) and get
  its BNS mapping, offense type, bailable status, punishment, and process
  guidance, backed by a seeded knowledge base and an optional LLM.
- **Case management** — file ongoing cases, look up cases by Aadhaar, track
  bail status, record judgments as completed cases.
- **Advocate discovery** — find legal aid providers near a location, filtered
  by fee and experience, ranked by Haversine distance.
- **Judicial collaboration** — pending-case and pending-opinion queues,
  opinions, suggestions, and case take-up by legal aid providers.
- **Historical analytics** — search past judgments by IPC codes.

## Architecture

One FastAPI process serves both the JSON API (under `/api`) and the frontend
(Jinja2 templates + static assets). SQLite by default; PostgreSQL in
production via `DATABASE_URL`.

```
app/
├── main.py              # FastAPI app: routers, static mount, startup seeding
├── core/
│   ├── config.py        # pydantic-settings; all configuration via .env
│   └── security.py      # bcrypt hashing, JWT create/verify, auth dependency
├── db/
│   ├── base.py          # SQLAlchemy DeclarativeBase
│   ├── session.py       # engine, session factory, get_db dependency
│   └── seed.py          # idempotent knowledge-base seeding
├── models/              # SQLAlchemy 2.0 models (users, cases, legal sections)
├── schemas/             # Pydantic request/response models
├── services/            # business logic
│   └── ai/              # provider-agnostic AI layer (see below)
└── api/routes/          # auth, cases, providers, legal, pages
frontend/
├── templates/           # HTML pages served at /<page-name>
└── static/              # css/, js/, images/
data/ipc_sections.csv    # seed data for the legal knowledge base
scripts/seed_db.py       # standalone table-create + seed script
tests/                   # pytest suite (SQLite in-memory, no externals)
```

### AI provider abstraction

`POST /api/get-bail-status` answers from the `legal_sections` knowledge base
and enriches the response through a pluggable provider chain
(`app/services/ai/`):

| Provider | Cost | Setup |
|---|---|---|
| `rule_based` (default) | Free, offline | None — answers deterministically from the knowledge base |
| `ollama` | Free, local | Install [Ollama](https://ollama.com), `ollama pull llama3.2` |
| `openrouter` | Free-tier models | `OPENROUTER_API_KEY` |
| `openai` | Paid | `OPENAI_API_KEY` |

Set `AI_PROVIDER` in `.env`. Whatever is selected, `rule_based` remains the
final fallback, so the feature always works with zero credentials. Adding a
new provider = implement `LegalInfoProvider` in `app/services/ai/` and register
it in `factory.py` — nothing else changes.

## Getting Started

Requirements: **Python 3.11 or 3.12**.

```bash
git clone https://github.com/Harshajevs/Bail-Reckoner.git
cd Bail-Reckoner

python3.12 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>. Tables are created and the IPC knowledge base is
seeded automatically on first startup. Interactive API docs:
<http://127.0.0.1:8000/docs>.

No `.env` is needed for local development. For production, copy
`.env.example` to `.env` and set at least `SECRET_KEY` (and `DATABASE_URL`
for PostgreSQL).

### Database setup (PostgreSQL, optional)

```bash
createdb bail_reckoner
echo 'DATABASE_URL=postgresql://user:password@localhost:5432/bail_reckoner' >> .env
python -m scripts.seed_db        # or just start the app; startup does the same
```

The `psycopg2-binary` driver in `requirements.txt` requires Python ≤ 3.13.
On newer Pythons, `pip install "psycopg[binary]"` and use a
`postgresql+psycopg://` URL instead.

### Running AI services (optional)

```bash
# Local LLM, fully free/offline:
ollama pull llama3.2
echo 'AI_PROVIDER=ollama' >> .env

# Or hosted free models:
echo 'AI_PROVIDER=openrouter' >> .env
echo 'OPENROUTER_API_KEY=sk-or-...' >> .env
```

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

The suite (32 tests) covers auth, the full case lifecycle, provider discovery,
the AI legal-info flow, and page serving. It runs against an in-memory SQLite
database — no external services or API keys required.

## API Overview

All endpoints are under `/api`. Endpoints marked 🔒 require
`Authorization: Bearer <token>` from `POST /api/login`.

| Endpoint | Purpose |
|---|---|
| `POST /register`, `POST /login` | Account creation, JWT login |
| 🔒 `POST /add-ongoing-case`, `POST /add-completed-case` | File cases |
| 🔒 `GET /ongoing-cases`, `GET /completed-cases` | Paginated case lists |
| 🔒 `GET /validate-aadhar/{aadhar}` | Prisoner case lookup |
| 🔒 `GET /ongoing-cases/{aadhar}`, `/completed-cases/{aadhar}`, `/all-cases/{aadhar}` | Counts and consolidated view |
| 🔒 `GET /pending-cases`, `GET /pending-opinions` | Work queues |
| 🔒 `POST /take-up-case/{id}`, `/submit-opinion/{id}`, `/suggestion/{id}` | Case actions |
| 🔒 `POST /historical-cases` | Judgment search by IPC codes |
| `POST /get-bail-status` | Bail eligibility + AI guidance (public, used by guest page) |
| `POST /get-nearest-providers`, `GET /get-provider-location/{id}` | Advocate discovery (public) |
| `GET /api/health` | Health check |

## Environment Variables

See [`.env.example`](.env.example) for the full annotated list:
`DATABASE_URL`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `CORS_ORIGINS`,
`AI_PROVIDER`, and per-provider settings (`OLLAMA_*`, `OPENROUTER_*`,
`OPENAI_*`).

## Deployment (free tiers)

Recommended: **Render (web service) + Neon (PostgreSQL)** — both have
persistent free tiers and need no credit card.

1. Create a free PostgreSQL database on [Neon](https://neon.tech); copy the
   connection string.
2. On [Render](https://render.com), create a Web Service from this repo:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment: `DATABASE_URL` (Neon string), `SECRET_KEY` (random 64-hex).
3. First deploy creates tables and seeds the knowledge base automatically.

Alternatives: Railway or Fly.io (same start command); Hugging Face Spaces
(Docker) if you also want to co-host an open-source LLM. Vercel/Cloudflare
Pages are not a fit — this is a long-running Python server, not an edge
function.

Free-tier limitations: Render free instances sleep after idle (cold starts
~30s); Neon free tier suspends compute when idle; SQLite on ephemeral
filesystems loses data across deploys — use Postgres in any hosted setup. For
LLM enrichment in hosted deployments, prefer `openrouter` free models (Ollama
needs a machine of its own).

## Troubleshooting

- **`pip install` fails on `psycopg2-binary`** — you're on Python ≥ 3.14; see
  the PostgreSQL note above, or use Python 3.12.
- **401 on every case endpoint** — the frontend attaches the JWT from
  `localStorage` (`frontend/static/js/auth.js`); log in again if the token
  expired (12h default).
- **AI answers are terse** — you're on the default `rule_based` provider;
  configure `ollama` or `openrouter` for generated guidance.
- **`Invalid IPC section format`** — the lookup expects `IPC_XXX`
  (e.g. `IPC_302`).
- **Postgres `SSL` errors on Neon** — append `?sslmode=require` to
  `DATABASE_URL`.

## Security Notes

- Do not commit `.env`. The old repository history contained credentials —
  any keys that ever appeared there must be considered compromised and revoked.
- Aadhaar numbers are demo-grade plaintext; a real deployment needs
  encryption at rest, masking in responses, and a data-protection review.
- The admin login on the login page is a client-side demo stub, not a real
  account system.

## Future Improvements

- Alembic migrations (schema is currently `create_all`-managed).
- Role-based authorization per endpoint (any logged-in user can currently call
  any protected endpoint, matching original behavior).
- Semantic/vector search over historical judgments (the original pgvector
  integration was initialized but unused; reintroduce behind the AI provider
  abstraction if needed).
- Replace the demo admin stub with a real admin role.
- Pagination/filtering on work-queue endpoints; image compression for the
  large background JPEGs.
