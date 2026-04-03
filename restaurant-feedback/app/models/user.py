from flask_login import UserMixin

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(120), nullable=False)
    avatar_url = db.Column(db.String(512), default="")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    reviews = db.relationship("Review", backref="author", lazy="dynamic")
    dishes_added = db.relationship("Dish", backref="added_by_user", lazy="dynamic")
