from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import login_user, logout_user

from app.models import User, db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

_oauth_registry = None


def _get_oauth():
    """Lazy-init Authlib OAuth registry."""
    global _oauth_registry
    if _oauth_registry is None:
        from authlib.integrations.flask_client import OAuth

        _oauth_registry = OAuth(current_app._get_current_object())
        provider_url = current_app.config["OIDC_PROVIDER_URL"]
        if provider_url:
            _oauth_registry.register(
                name="oidc",
                client_id=current_app.config["OIDC_CLIENT_ID"],
                client_secret=current_app.config["OIDC_CLIENT_SECRET"],
                server_metadata_url=f"{provider_url.rstrip('/')}/.well-known/openid-configuration",
                client_kwargs={"scope": "openid email profile"},
            )
    return _oauth_registry


def _oidc_configured():
    return bool(
        current_app.config.get("OIDC_PROVIDER_URL")
        and current_app.config.get("OIDC_CLIENT_ID")
    )


@auth_bp.route("/login")
def login():
    if _oidc_configured():
        oauth = _get_oauth()
        redirect_uri = url_for("auth.callback", _external=True)
        return oauth.oidc.authorize_redirect(redirect_uri)
    # Fallback: show a simple demo-login form
    return render_template("login.html")


@auth_bp.route("/login/demo", methods=["POST"])
def demo_login():
    """Quick demo login — no real auth, just picks/creates a user by email."""
    email = request.form.get("email", "").strip().lower()
    name = request.form.get("name", "").strip()
    if not email or not name:
        flash("Email and name are required.", "error")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(email=email, display_name=name)
        db.session.add(user)
        db.session.commit()
    login_user(user)
    flash(f"Welcome, {user.display_name}!", "success")
    return redirect(url_for("main.index"))


@auth_bp.route("/callback")
def callback():
    oauth = _get_oauth()
    token = oauth.oidc.authorize_access_token()
    userinfo = token.get("userinfo") or oauth.oidc.userinfo()

    email = userinfo["email"]
    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(
            email=email,
            display_name=userinfo.get("name", email.split("@")[0]),
            avatar_url=userinfo.get("picture", ""),
        )
        db.session.add(user)
        db.session.commit()
    else:
        user.display_name = userinfo.get("name", user.display_name)
        user.avatar_url = userinfo.get("picture", user.avatar_url)
        db.session.commit()

    login_user(user)
    flash(f"Welcome, {user.display_name}!", "success")
    return redirect(url_for("main.index"))


@auth_bp.route("/logout")
def logout():
    logout_user()
    session.clear()
    flash("You've been logged out.", "info")
    return redirect(url_for("main.index"))
