# Execution Plan — Bail Reckoner Modernization

Each phase is small, independently testable, and lands as one or more focused
commits. Legacy files are removed only after their replacement is verified.

---

## Phase 0 — Repo Hygiene

- **Objective:** Make the repository clean and reviewable before code changes.
- **Scope:** Add `.gitignore`; delete committed `__pycache__/`, empty `pgvector/`
  dir, empty templates (`approve.html`, `users.html`, `ongoing_cases.html`),
  duplicate `about1.html`; add `docs/` (audit, PRD, this plan).
- **Files affected:** deletions + new docs; no runtime code.
- **Risks:** None (artifacts are unreferenced — verified by grep).
- **Testing:** `git status` clean; legacy apps unaffected.
- **Rollback:** `git revert` of the commit.

## Phase 1 — Application Skeleton & Configuration

- **Objective:** A single FastAPI app with env-driven config that boots.
- **Scope:** `app/main.py`, `app/core/config.py` (pydantic-settings, `.env`
  support, SQLite default), `app/db/{base,session}.py`, `.env.example`,
  new pinned `requirements.txt`.
- **Risks:** Dependency pin conflicts → verified by clean install in a fresh venv.
- **Testing:** App starts; `/api/health` returns 200.
- **Rollback:** Legacy apps still present and untouched.

## Phase 2 — Data Model Unification

- **Objective:** One set of SQLAlchemy 2.0 models replacing the two divergent copies.
- **Scope:** `app/models/` — `Prisoner`, `LegalAidProvider`, `JudicialAuthority`,
  `OngoingCase`, `CompletedCase`, `LegalSection` (knowledge base). Fixes applied:
  FK from cases → prisoners/providers, `legal_aid_provider_id` stays Integer and
  receives the provider **id** (was: license string — type bug), `Opinion` →
  `opinion`, indexes on `aadhar_number`, timezone-aware timestamps.
- **Risks:** Schema drift from legacy DBs — acceptable per PRD assumption (demo
  data); documented in README.
- **Testing:** `create_all` on SQLite + Postgres; model unit checks in test suite.
- **Rollback:** Models are additive at this phase.

## Phase 3 — Auth (register + login + JWT)

- **Objective:** Port Flask registration and FastAPI login into one router with
  real token-based auth.
- **Scope:** `app/core/security.py`, `app/schemas/auth.py`, `app/services/auth.py`,
  `app/api/routes/auth.py`. Role-specific registration preserved (same fields);
  login now returns a JWT carrying role + subject; `get_current_user` dependency
  protects PII endpoints.
- **Risks:** Frontend expects old response shape → login response keeps
  `message`/`name`/`role` fields and adds `access_token`.
- **Testing:** Register/login/reject-wrong-password tests for all three roles.
- **Rollback:** Legacy endpoints remain until Phase 7.

## Phase 4 — Case Management & Provider Discovery

- **Objective:** Port all case and advocate-discovery endpoints, de-duplicated.
- **Scope:** `app/schemas/cases.py`, `app/services/{cases,providers}.py`,
  `app/api/routes/{cases,providers}.py`. Endpoint mapping preserved 1:1 under
  `/api` (documented in README table). Fixes: proper date types via Pydantic,
  serialization via schemas (no `__dict__` dumps), take-up stores provider id,
  count/list endpoints paginated where unbounded.
- **Risks:** Behavior drift → parity checklist from audit §4; response shapes kept.
- **Testing:** Route-group tests: add/list/lookup ongoing + completed cases,
  pending queues, take-up, opinions, historical search, nearest providers.
- **Rollback:** Per-router revert; legacy still present.

## Phase 5 — AI Legal-Info Layer

- **Objective:** Replace hardcoded OpenAI with a provider abstraction + free default.
- **Scope:** `app/services/ai/` (base interface, rule_based, ollama, openrouter,
  openai, factory), `app/api/routes/legal.py`, `data/ipc_sections.csv`,
  `scripts/seed_db.py`. `POST /api/legal/bail-info` preserves the old
  `/get-bail-status` contract (markdown-ish text response).
- **Risks:** LLM providers unreachable → factory falls back to rule-based, which
  answers purely from the seeded knowledge table.
- **Testing:** Rule-based provider tests (section found / not found); factory
  fallback test; endpoint contract test. Remote providers behind env flags.
- **Rollback:** Feature is self-contained behind one route.

## Phase 6 — Frontend Restructure

- **Objective:** Serve the UI from the app; kill hardcoded hosts and file:// nav.
- **Scope:** Move HTML → `frontend/templates/`, CSS → `frontend/static/css/`;
  page routes (`/`, `/login`, `/register`, `/home`, role dashboards…); rewrite
  `http://127.0.0.1:8000|5000/...` → relative `/api/...`; `window.location`
  targets → served routes; store JWT after login and send it on API calls.
- **Risks:** Missed URL → post-rewrite grep for `127.0.0.1|localhost|\.html'`;
  manual walk of every page.
- **Testing:** Page routes return 200 with correct templates; smoke test of the
  register→login→lookup flow through served pages.
- **Rollback:** Old `templates/` retained in git history.

## Phase 7 — Legacy Removal & Code Quality

- **Objective:** Delete `app.py`, `main.py`, `ongoing.py`, `backend_code.py`,
  `query3.py`, `database.py`, `database_setup.py`, `extensions.py`, `models.py`,
  old `templates/` after parity verification.
- **Risks:** Removing something still referenced → full-repo grep before delete;
  test suite green after.
- **Testing:** Full test suite + manual end-to-end pass.
- **Rollback:** Single revertable commit.

## Phase 8 — Tests, Docs & Deployment Guide

- **Objective:** Meet PRD success criteria.
- **Scope:** Complete `tests/`; rewrite `README.md` (setup, env vars, run, test,
  structure, troubleshooting, deployment on free tiers, future work); credentials
  checklist.
- **Testing:** Fresh-clone dry run of README instructions.

---

**Commit conventions:** one logical change per commit, imperative messages,
no attribution metadata.
