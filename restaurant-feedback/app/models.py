from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(120), nullable=False)
    avatar_url = db.Column(db.String(512), default="")
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    reviews = db.relationship("Review", backref="author", lazy="dynamic")
    dishes_added = db.relationship("Dish", backref="added_by_user", lazy="dynamic")


class Restaurant(db.Model):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)
    google_place_id = db.Column(db.String(300), unique=True, nullable=True, index=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    dishes = db.relationship(
        "Dish", backref="restaurant", lazy="dynamic", cascade="all, delete-orphan"
    )

    @property
    def avg_rating(self):
        ratings = [d.avg_rating for d in self.dishes if d.avg_rating is not None]
        return round(sum(ratings) / len(ratings), 1) if ratings else None

    @property
    def review_count(self):
        return sum(d.review_count for d in self.dishes)


class Dish(db.Model):
    __tablename__ = "dishes"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurants.id"), nullable=False, index=True
    )
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), default="")
    added_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    reviews = db.relationship(
        "Review", backref="dish", lazy="dynamic", cascade="all, delete-orphan"
    )

    @property
    def avg_rating(self):
        ratings = [r.rating for r in self.reviews]
        return round(sum(ratings) / len(ratings), 1) if ratings else None

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def recommendation_pct(self):
        reviews = list(self.reviews)
        if not reviews:
            return None
        recommended = sum(1 for r in reviews if r.would_recommend)
        return round(recommended / len(reviews) * 100)


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    dish_id = db.Column(
        db.Integer, db.ForeignKey("dishes.id"), nullable=False, index=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text, default="")
    would_recommend = db.Column(db.Boolean, default=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        db.UniqueConstraint("dish_id", "user_id", name="one_review_per_dish_per_user"),
    )
