from app.extensions import db


class Dish(db.Model):
    __tablename__ = "dishes"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurants.id"), nullable=False, index=True
    )
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), default="")
    added_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

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
