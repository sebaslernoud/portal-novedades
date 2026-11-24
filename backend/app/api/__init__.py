"""Rutas de la API. Todo cuelga de /api."""

from flask import Blueprint

api = Blueprint("api", __name__, url_prefix="/api")

from app.api import salud  # noqa: E402, F401  (registra las rutas en el blueprint)
