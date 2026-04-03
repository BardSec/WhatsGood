from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.blueprints.main import bp
from app.extensions import db
from app.models import Dish, Restaurant
from app.services import restaurant_service


@bp.route("/")
def index():
    q = request.args.get("q", "").strip()
    if q:
        restaurants = restaurant_service.search_restaurants(q)
    else:
        restaurants = restaurant_service.get_all_restaurants()
    return render_template("index.html", restaurants=restaurants, query=q)


@bp.route("/restaurant/<int:restaurant_id>")
def restaurant_detail(restaurant_id):
    restaurant = db.get_or_404(Restaurant, restaurant_id)
    dishes = restaurant.dishes.order_by(Dish.created_at.desc()).all()
    return render_template("restaurant.html", restaurant=restaurant, dishes=dishes)


@bp.route("/restaurant/add", methods=["GET", "POST"])
@login_required
def add_restaurant():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        address = request.form.get("address", "").strip()
        if not name or not address:
            flash("Restaurant name and address are required.", "error")
            return redirect(url_for("main.add_restaurant"))

        restaurant = restaurant_service.create_restaurant(
            name=name,
            address=address,
            lat=request.form.get("lat", type=float),
            lng=request.form.get("lng", type=float),
            google_place_id=request.form.get("place_id", "").strip(),
        )
        flash(f"Added {restaurant.name}!", "success")
        return redirect(url_for("main.restaurant_detail", restaurant_id=restaurant.id))
    return render_template("add_restaurant.html")


@bp.route("/restaurant/<int:restaurant_id>/dish/add", methods=["POST"])
@login_required
def add_dish(restaurant_id):
    restaurant = db.get_or_404(Restaurant, restaurant_id)
    name = request.form.get("name", "").strip()
    if not name:
        flash("Dish name is required.", "error")
        return redirect(url_for("main.restaurant_detail", restaurant_id=restaurant.id))

    dish = restaurant_service.add_dish(
        restaurant_id=restaurant.id,
        name=name,
        description=request.form.get("description", "").strip(),
        added_by=current_user.id,
    )
    flash(f"Added {dish.name} to the menu!", "success")
    return redirect(url_for("main.restaurant_detail", restaurant_id=restaurant.id))


@bp.route("/dish/<int:dish_id>/review", methods=["POST"])
@login_required
def add_review(dish_id):
    dish = db.get_or_404(Dish, dish_id)
    rating = request.form.get("rating", type=int)
    if not rating or rating < 1 or rating > 5:
        flash("Rating must be between 1 and 5.", "error")
        return redirect(url_for("main.restaurant_detail", restaurant_id=dish.restaurant_id))

    review = restaurant_service.add_review(
        dish_id=dish.id,
        user_id=current_user.id,
        rating=rating,
        comment=request.form.get("comment", "").strip(),
        would_recommend=request.form.get("would_recommend") == "on",
    )
    if review is None:
        flash("You've already reviewed this dish. You can edit your review instead.", "error")
    else:
        flash("Review submitted — thanks for sharing!", "success")
    return redirect(url_for("main.restaurant_detail", restaurant_id=dish.restaurant_id))


@bp.route("/dish/<int:dish_id>/review/edit", methods=["POST"])
@login_required
def edit_review(dish_id):
    dish = db.get_or_404(Dish, dish_id)
    rating = request.form.get("rating", type=int)
    if not rating or rating < 1 or rating > 5:
        flash("Rating must be between 1 and 5.", "error")
        return redirect(url_for("main.restaurant_detail", restaurant_id=dish.restaurant_id))

    restaurant_service.update_review(
        dish_id=dish.id,
        user_id=current_user.id,
        rating=rating,
        comment=request.form.get("comment", "").strip(),
        would_recommend=request.form.get("would_recommend") == "on",
    )
    flash("Review updated!", "success")
    return redirect(url_for("main.restaurant_detail", restaurant_id=dish.restaurant_id))


@bp.route("/api/restaurants/search")
def api_search():
    """JSON endpoint for live search."""
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify([])
    results = restaurant_service.search_restaurants(q, limit=10)
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
