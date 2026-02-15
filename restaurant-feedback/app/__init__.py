import os

from flask import Flask
from flask_login import LoginManager

from config import Config

login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    from app.models import db

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User

        return db.session.get(User, int(user_id))

    from app.auth import auth_bp
    from app.routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        _seed_demo_data(db)

    return app


def _seed_demo_data(db):
    """Insert sample restaurants and dishes if the database is empty."""
    from app.models import Dish, Restaurant

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
