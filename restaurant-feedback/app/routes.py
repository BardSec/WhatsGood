from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models import Dish, Restaurant, Review, db

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    q = request.args.get("q", "").strip()
    if q:
        restaurants = Restaurant.query.filter(
            Restaurant.name.ilike(f"%{q}%")
            | Restaurant.address.ilike(f"%{q}%")
        ).all()
    else:
        restaurants = Restaurant.query.order_by(Restaurant.created_at.desc()).all()
    return render_template("index.html", restaurants=restaurants, query=q)


@main_bp.route("/restaurant/<int:restaurant_id>")
def restaurant_detail(restaurant_id):
    restaurant = db.get_or_404(Restaurant, restaurant_id)
    dishes = restaurant.dishes.order_by(Dish.created_at.desc()).all()
    return render_template(
        "restaurant.html", restaurant=restaurant, dishes=dishes
    )


@main_bp.route("/restaurant/add", methods=["GET", "POST"])
@login_required
def add_restaurant():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        address = request.form.get("address", "").strip()
        if not name or not address:
            flash("Restaurant name and address are required.", "error")
            return redirect(url_for("main.add_restaurant"))

        restaurant = Restaurant(
            name=name,
            address=address,
            lat=request.form.get("lat", type=float),
            lng=request.form.get("lng", type=float),
            google_place_id=request.form.get("place_id", "").strip() or None,
        )
        db.session.add(restaurant)
        db.session.commit()
        flash(f"Added {restaurant.name}!", "success")
        return redirect(url_for("main.restaurant_detail", restaurant_id=restaurant.id))
    return render_template("add_restaurant.html")


@main_bp.route("/restaurant/<int:restaurant_id>/dish/add", methods=["POST"])
@login_required
def add_dish(restaurant_id):
    restaurant = db.get_or_404(Restaurant, restaurant_id)
    name = request.form.get("name", "").strip()
    if not name:
        flash("Dish name is required.", "error")
        return redirect(url_for("main.restaurant_detail", restaurant_id=restaurant.id))

    dish = Dish(
        restaurant_id=restaurant.id,
        name=name,
        description=request.form.get("description", "").strip(),
        added_by=current_user.id,
    )
    db.session.add(dish)
    db.session.commit()
    flash(f"Added {dish.name} to the menu!", "success")
    return redirect(url_for("main.restaurant_detail", restaurant_id=restaurant.id))


@main_bp.route("/dish/<int:dish_id>/review", methods=["POST"])
@login_required
def add_review(dish_id):
    dish = db.get_or_404(Dish, dish_id)

    existing = Review.query.filter_by(
        dish_id=dish.id, user_id=current_user.id
    ).first()
    if existing:
        flash("You've already reviewed this dish. You can edit your review instead.", "error")
        return redirect(
            url_for("main.restaurant_detail", restaurant_id=dish.restaurant_id)
        )

    rating = request.form.get("rating", type=int)
    if not rating or rating < 1 or rating > 5:
        flash("Rating must be between 1 and 5.", "error")
        return redirect(
            url_for("main.restaurant_detail", restaurant_id=dish.restaurant_id)
        )

    review = Review(
        dish_id=dish.id,
        user_id=current_user.id,
        rating=rating,
        comment=request.form.get("comment", "").strip(),
        would_recommend=request.form.get("would_recommend") == "on",
    )
    db.session.add(review)
    db.session.commit()
    flash("Review submitted — thanks for sharing!", "success")
    return redirect(
        url_for("main.restaurant_detail", restaurant_id=dish.restaurant_id)
    )


@main_bp.route("/dish/<int:dish_id>/review/edit", methods=["POST"])
@login_required
def edit_review(dish_id):
    dish = db.get_or_404(Dish, dish_id)
    review = Review.query.filter_by(
        dish_id=dish.id, user_id=current_user.id
    ).first_or_404()

    rating = request.form.get("rating", type=int)
    if not rating or rating < 1 or rating > 5:
        flash("Rating must be between 1 and 5.", "error")
        return redirect(
            url_for("main.restaurant_detail", restaurant_id=dish.restaurant_id)
        )

    review.rating = rating
    review.comment = request.form.get("comment", "").strip()
    review.would_recommend = request.form.get("would_recommend") == "on"
    db.session.commit()
    flash("Review updated!", "success")
    return redirect(
        url_for("main.restaurant_detail", restaurant_id=dish.restaurant_id)
    )


@main_bp.route("/api/restaurants/search")
def api_search():
    """JSON endpoint for live search."""
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify([])
    results = Restaurant.query.filter(
        Restaurant.name.ilike(f"%{q}%") | Restaurant.address.ilike(f"%{q}%")
    ).limit(10).all()
    return jsonify(
        [
            {
                "id": r.id,
                "name": r.name,
                "address": r.address,
                "avg_rating": r.avg_rating,
                "review_count": r.review_count,
            }
            for r in results
        ]
    )
