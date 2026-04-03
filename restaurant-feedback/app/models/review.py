from app.extensions import db


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    dish_id = db.Column(
        db.Integer, db.ForeignKey("dishes.id"), nullable=False, index=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, default="")
    would_recommend = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (
        db.UniqueConstraint("dish_id", "user_id", name="one_review_per_dish_per_user"),
    )
