from app.extensions import db


class Restaurant(db.Model):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)
    google_place_id = db.Column(db.String(300), unique=True, nullable=True, index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

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
