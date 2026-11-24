"""Migración inicial: línea de base, sin tablas de negocio.

Deja creada la tabla alembic_version para que /api/salud informe la revisión. Las tablas de
empleados, solicitudes, aprobaciones y auditoría se agregan en migraciones siguientes.

Revision ID: 0001
Revises:
Create Date: 2026-11-24
"""
from collections.abc import Sequence

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
