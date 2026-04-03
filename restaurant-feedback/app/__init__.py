from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from app.extensions import db, migrate, login_manager, csrf


def create_app(config_class=None):
    if config_class is None:
        from config import Config
        config_class = Config

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Trust proxy headers (Cloudflare Tunnel / reverse proxy)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.main import bp as main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # User loader
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    return app
