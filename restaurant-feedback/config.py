import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://whatsgood:whatsgood@db:5432/whatsgood",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OIDC / OAuth2 (leave unset for dev login fallback)
    OIDC_PROVIDER_URL = os.environ.get("OIDC_PROVIDER_URL", "")
    OIDC_CLIENT_ID = os.environ.get("OIDC_CLIENT_ID", "")
    OIDC_CLIENT_SECRET = os.environ.get("OIDC_CLIENT_SECRET", "")
