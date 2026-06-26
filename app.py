from flask import Flask
from controllers.auth import auth
from controllers.products import products
from errors import register_error_handlers
from models import db


def create_app(test_config=None):
    app = Flask(__name__)

    app.json.sort_keys = False

    app.config.from_mapping(SQLALCHEMY_DATABASE_URI="sqlite:///database.db")

    if test_config is None:
        app.config.from_prefixed_env()
    else:
        app.config.from_mapping(test_config)

    db.init_app(app)

    app.register_blueprint(auth)
    app.register_blueprint(products)

    register_error_handlers(app)
    return app
