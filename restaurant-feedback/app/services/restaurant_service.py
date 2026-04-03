from app.extensions import db
from app.models.restaurant import Restaurant
from app.models.dish import Dish
from app.models.review import Review


def search_restaurants(query, limit=None):
    """Search restaurants by name or address."""
    q = Restaurant.query.filter(
        Restaurant.name.ilike(f"%{query}%")
        | Restaurant.address.ilike(f"%{query}%")
    )
    if limit:
        q = q.limit(limit)
    return q.all()


def get_all_restaurants():
    return Restaurant.query.order_by(Restaurant.created_at.desc()).all()


def create_restaurant(name, address, lat=None, lng=None, google_place_id=None):
    restaurant = Restaurant(
        name=name,
        address=address,
        lat=lat,
        lng=lng,
        google_place_id=google_place_id or None,
    )
    db.session.add(restaurant)
    db.session.commit()
    return restaurant


def add_dish(restaurant_id, name, description="", added_by=None):
    dish = Dish(
        restaurant_id=restaurant_id,
        name=name,
        description=description,
        added_by=added_by,
    )
    db.session.add(dish)
    db.session.commit()
    return dish


def add_review(dish_id, user_id, rating, comment="", would_recommend=True):
    existing = Review.query.filter_by(dish_id=dish_id, user_id=user_id).first()
    if existing:
        return None

    review = Review(
        dish_id=dish_id,
        user_id=user_id,
        rating=rating,
        comment=comment,
        would_recommend=would_recommend,
    )
    db.session.add(review)
    db.session.commit()
    return review


def update_review(dish_id, user_id, rating, comment="", would_recommend=True):
    review = Review.query.filter_by(dish_id=dish_id, user_id=user_id).first()
    if not review:
        return None

    review.rating = rating
    review.comment = comment
    review.would_recommend = would_recommend
    db.session.commit()
    return review


def seed_demo_data():
    """Insert sample restaurants and dishes if the database is empty."""
    if Restaurant.query.first() is not None:
        return

    samples = [
        {
            "name": "Mama Rosa's Italian Kitchen",
            "address": "142 Elm Street, Brooklyn, NY 11201",
            "lat": 40.6892,
            "lng": -73.9857,
            "dishes": [
                ("Truffle Mac & Cheese", "Four-cheese blend with black truffle oil"),
                ("Margherita Pizza", "San Marzano tomatoes, fresh mozzarella, basil"),
                ("Tiramisu", "Classic ladyfinger and mascarpone dessert"),
            ],
        },
        {
            "name": "Golden Dragon",
            "address": "88 Mott Street, New York, NY 10013",
            "lat": 40.7158,
            "lng": -73.9970,
            "dishes": [
                ("Xiao Long Bao", "Soup dumplings with pork filling"),
                ("Mapo Tofu", "Silken tofu in spicy Sichuan sauce"),
                ("Scallion Pancakes", "Pan-fried crispy flatbread"),
            ],
        },
        {
            "name": "Big Tex BBQ",
            "address": "501 Congress Ave, Austin, TX 78701",
            "lat": 30.2672,
            "lng": -97.7431,
            "dishes": [
                ("Brisket Plate", "14-hour smoked beef brisket with two sides"),
                ("Pulled Pork Sandwich", "Hickory-smoked pork with tangy slaw"),
                ("Mac & Cheese", "Smoked gouda and cheddar baked mac"),
            ],
        },
        {
            "name": "Sakura Sushi",
            "address": "920 Wilshire Blvd, Los Angeles, CA 90017",
            "lat": 34.0522,
            "lng": -118.2437,
            "dishes": [
                ("Omakase Platter", "Chef's choice 12-piece nigiri selection"),
                ("Spicy Tuna Roll", "Fresh tuna with sriracha mayo and tempura flakes"),
                ("Miso Ramen", "Rich pork broth with chashu and soft egg"),
            ],
        },
        {
            "name": "Le Petit Bistro",
            "address": "37 Magazine Street, New Orleans, LA 70130",
            "lat": 29.9511,
            "lng": -90.0715,
            "dishes": [
                ("Shrimp & Grits", "Cajun shrimp over stone-ground grits"),
                ("Crème Brûlée", "Vanilla bean custard with caramelized sugar"),
                ("French Onion Soup", "Caramelized onion broth with gruyère crouton"),
            ],
        },
    ]

    for data in samples:
        restaurant = Restaurant(
            name=data["name"],
            address=data["address"],
            lat=data["lat"],
            lng=data["lng"],
        )
        db.session.add(restaurant)
        db.session.flush()
        for dish_name, dish_desc in data["dishes"]:
            db.session.add(
                Dish(
                    restaurant_id=restaurant.id,
                    name=dish_name,
                    description=dish_desc,
                )
            )

    db.session.commit()
