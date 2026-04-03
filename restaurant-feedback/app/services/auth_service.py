from app.extensions import db
from app.models.user import User


def get_or_create_user(email, display_name="", avatar_url=""):
    """Find existing user by email or create a new one."""
    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(
            email=email,
            display_name=display_name or email.split("@")[0],
            avatar_url=avatar_url,
        )
        db.session.add(user)
        db.session.commit()
    return user


def update_user_profile(user, display_name=None, avatar_url=None):
    """Update user profile from SSO provider info."""
    if display_name:
        user.display_name = display_name
    if avatar_url:
        user.avatar_url = avatar_url
    db.session.commit()
    return user
