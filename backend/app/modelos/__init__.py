"""Modelos de SQLAlchemy.

Importar acá cada módulo de modelos nuevo para que Alembic los vea al generar migraciones
(`alembic revision --autogenerate`). Todavía no hay modelos de negocio: se definen cuando se
resuelva la Fase 0 (ver CLAUDE.md).
"""

from app.db import Base

__all__ = ["Base"]
