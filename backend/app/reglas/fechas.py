"""Fechas de negocio: siempre `date` (sin hora) para evitar corrimientos de zona horaria."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.config import Config

ZONA_NEGOCIO = ZoneInfo(Config.TZ_NEGOCIO)


def ahora_negocio() -> datetime:
    return datetime.now(ZONA_NEGOCIO)


def hoy_negocio() -> date:
    return ahora_negocio().date()


def formatear(fecha: date) -> str:
    return f"{fecha.day:02d}/{fecha.month:02d}/{fecha.year}"


def dias_inclusivos(desde: date, hasta: date) -> int:
    return (hasta - desde).days + 1


def diferencia_dias(a: date, b: date) -> int:
    """Días corridos de `a` a `b` (b − a)."""
    return (b - a).days
