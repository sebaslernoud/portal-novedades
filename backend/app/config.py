"""Configuración leída de variables de entorno."""

import os


def _activo(nombre: str) -> bool:
    return os.environ.get(nombre, "").strip().lower() in {"1", "true", "si", "sí"}


class Config:
    DATABASE_URL = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://portal:portal@localhost:5432/portal_novedades",
    )
    # Zona horaria del negocio: "hoy" para AnioNovedad/mesNovedad y para las advertencias de fechas.
    TZ_NEGOCIO = os.environ.get("TZ_NEGOCIO", "America/Argentina/Buenos_Aires")
    SECRET_KEY = os.environ.get("SECRET_KEY", "solo-para-desarrollo")
    # Mientras no haya login, el usuario sale del header X-Legajo-Prueba y de un directorio ficticio.
    # Nunca activarlo en producción: cualquiera podría hacerse pasar por cualquier legajo.
    IDENTIDAD_DE_PRUEBA = _activo("IDENTIDAD_DE_PRUEBA")
