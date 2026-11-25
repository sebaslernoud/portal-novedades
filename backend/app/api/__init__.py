"""Rutas de la API. Todo cuelga de /api."""

from flask import Blueprint, jsonify

from app.errores import ErrorApi

api = Blueprint("api", __name__, url_prefix="/api")


@api.errorhandler(ErrorApi)
def responder_error(error: ErrorApi):
    return jsonify(error.como_json()), error.status


# Registran las rutas en el blueprint.
from app.api import exportaciones, salud, solicitudes, usuarios  # noqa: E402, F401
