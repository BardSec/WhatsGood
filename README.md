# WhatsGood

A dish-level restaurant feedback app. Signed-in users add restaurants and dishes, then rate individual dishes (1 to 5 stars, a comment, and a "would recommend" flag). Anyone can browse restaurants and see average ratings and recommendation rates, so the answer to "what's good here?" comes from coworkers rather than generic review sites.

## Features

- Browse all restaurants, with a search box (name or address) and a live-search JSON endpoint
- Restaurant pages listing dishes with average rating, review count, and percent who would recommend
- Restaurant averages rolled up from their dishes
- Add restaurants (name and address) and add dishes to a restaurant's menu (requires login)
- One review per user per dish, editable afterward
- Sign-in through any OpenID Connect provider (e.g. Google or Microsoft Entra ID) via Authlib, falling back to a dev login (name and email, no password) when OIDC isn't configured
- CSRF protection on forms, plus `ProxyFix` for running behind a reverse proxy or Cloudflare Tunnel

The data model has optional latitude/longitude and Google Place ID fields on restaurants, but nothing populates them yet. A `seed_demo_data()` helper with sample restaurants exists in the service layer but isn't wired to a command.

## Tech stack

- Python 3.12, Flask 3.1, Gunicorn
- PostgreSQL 16, Flask-SQLAlchemy, Flask-Migrate
- Flask-Login, Authlib (OIDC), Flask-WTF (CSRF)
- Jinja2 templates, custom CSS, vanilla JavaScript
- Docker Compose

## Running

All app files are in `restaurant-feedback/`.

### Docker Compose

```bash
cd restaurant-feedback
cp .env.example .env      # then set SECRET_KEY, and OIDC values if using SSO
docker compose up -d --build
```

The app listens on port 8000. Compose starts both the app and PostgreSQL.

### Local development

```bash
cd restaurant-feedback
cp .env.example .env          # point DATABASE_URL at localhost if Postgres isn't in Compose
docker compose up -d db       # PostgreSQL only
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
flask db init                 # first time only; no migrations folder is committed yet
flask db migrate -m "initial schema"
flask db upgrade
flask run --host=0.0.0.0 --port=8000
```

## Environment variables

| Variable | Purpose |
|---|---|
| `FLASK_APP` | Flask entry point (`run.py`) |
| `SECRET_KEY` | Flask session signing key |
| `DATABASE_URL` | PostgreSQL connection string |
| `OIDC_PROVIDER_URL` | OIDC issuer base URL (discovery doc is read from `/.well-known/openid-configuration`). Leave unset for dev login |
| `OIDC_CLIENT_ID` | OIDC client ID |
| `OIDC_CLIENT_SECRET` | OIDC client secret |

## Project structure

```
CLAUDE.md                 Project notes for Claude Code
restaurant-feedback/
  run.py                  Entry point
  config.py               Config from environment
  gunicorn.conf.py
  app/
    __init__.py           App factory
    extensions.py         db, migrate, login_manager, csrf
    models/               User, Restaurant, Dish, Review
    blueprints/auth/      Login (OIDC or dev), callback, logout
    blueprints/main/      Restaurant, dish, and review routes plus search API
    services/             Auth and restaurant business logic
    templates/            Jinja2 templates
    static/               CSS and live-search JS
```

## Status

Early prototype. The Alembic migrations directory and tests haven't been committed yet (`tests/` is empty). There are no roles yet, so the "managers view aggregated feedback" idea in `CLAUDE.md` isn't built.
