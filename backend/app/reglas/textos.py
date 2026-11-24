"""Armado de textos de Observaciones."""

import re
import unicodedata
from collections.abc import Iterable
from datetime import date

from app.reglas.fechas import formatear


def unir_partes(partes: Iterable[str | None], separador: str = " ") -> str:
    return separador.join(p for p in partes if p is not None and p.strip() != "")


def normalizar_observaciones(texto: str | None) -> str | None:
    """Colapsa espacios. Nunca recorta: lo que escribió el empleado no se descarta."""
    if texto is None:
        return None
    limpio = re.sub(r"\s+", " ", texto).strip()
    return limpio or None


def lista_dias(fechas: Iterable[date | None]) -> str | None:
    """Texto "el día X" o "los días X, Y y Z", sin repetir y ordenados."""
    textos = [formatear(f) for f in sorted({f for f in fechas if f is not None})]
    if not textos:
        return None
    if len(textos) == 1:
        return f"el día {textos[0]}"
    return f"los días {', '.join(textos[:-1])} y {textos[-1]}"


def normalizar_nombre(nombre: str | None) -> str:
    """Sin acentos, en minúsculas, solo letras y con las palabras ordenadas: "Perez Juan" = "JUAN PEREZ"."""
    if not nombre:
        return ""
    sin_acentos = "".join(
        c for c in unicodedata.normalize("NFD", nombre) if not unicodedata.combining(c)
    ).lower()
    solo_letras = re.sub(r"[^a-z\s]", "", sin_acentos)
    return " ".join(sorted(solo_letras.split()))
