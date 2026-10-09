# CLAUDE.md

Guidance for Claude Code sessions in the HayalKız monorepo.

## Project

HayalKız — Telegram AI-companion bot (8 personas: chat, voice, selfies, videos, memory) + Telegram Mini App
(catalog, gift shop, Telegram Stars subscriptions). Markets: Türkiye and Russian-speaking users; UI ru/tr/en.

## Repository structure

Monorepo with git submodules (`git submodule update --init --recursive`):

| Path | Repo | What |
|---|---|---|
| `back/` | `giottobright/back` (private) | Python 3.12, aiogram 3, FastAPI, PostgreSQL + pgvector, Redis |
| `webapp/` | `giottobright/webapp` | React 18 + Vite Mini App |
| `docker-compose.yml` | this repo | full stack: bot + Mini App + Postgres + Redis (`docker compose --env-file back/.env up -d --build`) |

## Start here

All project documentation lives in the backend repo (this monorepo is public — do not put audits, vulnerability
details or secrets here):

1. `back/docs/PROJECT_STATUS.md` — current state, owner decisions, open tasks, workflow rules
2. `back/docs/ARCHITECTURE.md` — components, flows (webhook, Mini App auth, payments, limits), extension recipes
3. `back/docs/MODULES.md`, `back/docs/DATABASE.md` — module and schema reference
4. `back/CLAUDE.md`, `webapp/CLAUDE.md` — per-repo commands and conventions

## Rules

- Changes go through branches + pull requests in each submodule; never push to `main`/`master` directly.
  After submodule PRs merge, update the submodule pointers here in a separate PR.
- Never commit secrets, `.env` files, database dumps or VPN configs (see `.gitignore`).
- Backend: `pytest`, `ruff check .`, `scripts/check_secrets.sh`; webapp: `npm test && npm run build`.
