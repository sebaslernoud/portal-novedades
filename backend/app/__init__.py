"""Fábrica de la aplicación Flask."""

from flask import Flask

from app.config import Config
from app.db import iniciar_db


def crear_app(config: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)
    iniciar_db(app)

    from app.api import api

    app.register_blueprint(api)
    return app
