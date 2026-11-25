"""Modelos de SQLAlchemy.

Importar acá cada módulo de modelos nuevo para que Alembic los vea al generar migraciones
(`alembic revision --autogenerate`).
"""

from app.db import Base
from app.modelos.solicitud import (
    EstadoSolicitud,
    LoteExportacion,
    Novedad,
    RegistroAuditoria,
    Solicitud,
    TipoSolicitud,
)

__all__ = [
    "Base",
    "EstadoSolicitud",
    "LoteExportacion",
    "Novedad",
    "RegistroAuditoria",
    "Solicitud",
    "TipoSolicitud",
]
