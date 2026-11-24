"""GET /api/salud: estado del backend, de la base de datos y de las migraciones."""

from flask import jsonify
from sqlalchemy import text

from app.api import api
from app.db import sesion


@api.get("/salud")
def salud():
    try:
        sesion.execute(text("SELECT 1"))
        revision = sesion.execute(text("SELECT version_num FROM alembic_version")).scalar()
    except Exception:  # noqa: BLE001  (cualquier falla de conexión o de migración se informa igual)
        sesion.rollback()
        return jsonify(estado="error", base_de_datos="sin conexión o sin migrar"), 503
    return jsonify(estado="ok", base_de_datos="ok", migracion=revision)
