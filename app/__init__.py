from flask import Flask
from flask_jwt_extended import JWTManager
from .config import Config
from .utils.database import db
from .routes import auth, users, friends, locations, pings


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    JWTManager(app)

    # Register blueprints
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(users.bp, url_prefix='/users')
    app.register_blueprint(friends.bp, url_prefix='/friends')
    app.register_blueprint(locations.bp, url_prefix='/location')
    app.register_blueprint(pings.bp, url_prefix='/ping')

    with app.app_context():
        db.create_all()

    return app