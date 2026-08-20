# WhatsGood

Restaurant feedback platform. Employees submit restaurant reviews, managers view
aggregated feedback.

## Stack

- Python 3.12 / Flask 3.1 / Gunicorn 23.0
- PostgreSQL 16 + Flask-SQLAlchemy 3.1 + Flask-Migrate 4.0
- Flask-Login 0.6 + Authlib 1.4 (OIDC/OAuth2)
- Flask-WTF 1.2 (CSRF)
- Jinja2 + Bootstrap 5
- Docker Compose

## Project Layout

```
run.py              # Entry point
config.py           # Configuration (SECRET_KEY, DATABASE_URL, OIDC)
app/
  __init__.py       # App factory (create_app)
  extensions.py     # db, login_manager, oauth
  models/           # SQLAlchemy ORM models
  blueprints/       # Route blueprints
  services/         # Business logic
  templates/        # Jinja2 templates
  static/           # CSS, JS, images
```

## Dev Setup

```bash
cp .env.example .env
docker compose up -d                    # start PostgreSQL
pip install -r requirements.txt
flask db upgrade                        # run migrations
flask run --host=0.0.0.0 --port=8000    # dev server
```

## Key Patterns

- Single-tenant Flask archetype from global CLAUDE.md
- App factory pattern (`create_app()`)
- Service layer in `app/services/`
- OIDC/OAuth2 via Authlib — falls back to dev login when env vars unset
- Blueprint routing for modular routes

## Deploy

```bash
docker compose up -d    # PostgreSQL + Gunicorn (8 workers, 4 threads)
```

Gunicorn config in `gunicorn.conf.py`. Runs behind nginx/Cloudflare Tunnel.

## Running Tests

```bash
pytest
```
