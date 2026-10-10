# HayalKız

AI companion product for Telegram: a bot with eight AI personas (text, voice, selfies, short videos,
memory and daily life simulation) and a Mini App with a persona catalog, gift shop and Telegram Stars
subscriptions. Markets: Türkiye and Russian-speaking users; UI in Turkish, Russian and English.

| Part | Repository | Stack |
|---|---|---|
| `back/` | backend (private submodule) | Python 3.12, aiogram 3, FastAPI, PostgreSQL + pgvector, Redis |
| `webapp/` | Mini App (submodule) | React 18, Vite |

## Quick start

```bash
git clone --recurse-submodules https://github.com/giottobright/hayalkiz.git && cd hayalkiz
cp back/.env.example back/.env      # fill the required variables (the file explains each one)
docker compose --env-file back/.env up -d --build
```

- backend on `:8000` (health: `/healthz`), Mini App on `:8080`
- the database schema and reference content are created on first start
- configure the bot in @BotFather: Menu Button and Mini App URL → the Mini App address

Full documentation — deployment, configuration, content modes, plans and unit economics, payments,
operations — is in `back/README.md` (English) and `back/README.ru.md` (Russian).

## Highlights

- Telegram Stars: auto-renewing subscriptions, paid gifts, refunds, idempotent payment processing
- Server-side plans and limits with atomic usage accounting
- One OpenRouter key for all AI (chat, memory, selfies, video, voice); switchable content mode (SFW by default)
- Break-even pricing: Premium 750 ★, VIP 1500 ★, one-time packs (see `back/docs/PRICING.md`)
- 18+ age gate, content filter, data deletion on request, chat history retention
- Admin commands and revenue-vs-cost economics endpoint
- Tests and CI in both submodules

## License

Proprietary. All rights reserved.
