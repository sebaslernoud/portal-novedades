"""Configuración leída de variables de entorno."""

import os


class Config:
    DATABASE_URL = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://portal:portal@localhost:5432/portal_novedades",
    )
    # Zona horaria del negocio: "hoy" para AnioNovedad/mesNovedad y para las advertencias de fechas.
    TZ_NEGOCIO = os.environ.get("TZ_NEGOCIO", "America/Argentina/Buenos_Aires")
    SECRET_KEY = os.environ.get("SECRET_KEY", "solo-para-desarrollo")
