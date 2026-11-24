"""Solicitudes, auditoría del circuito y lotes de exportación a GMS (con sus novedades).

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-24 19:46:58.296427
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0002'
down_revision: str | None = '0001'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('lotes_exportacion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False),
    sa.Column('usuario_legajo', sa.Integer(), nullable=False),
    sa.Column('usuario_nombre', sa.String(length=120), nullable=False),
    sa.Column('nombre_archivo', sa.String(length=120), nullable=False),
    sa.Column('anio_novedad', sa.Integer(), nullable=False),
    sa.Column('mes_novedad', sa.Integer(), nullable=False),
    sa.Column('cantidad_filas', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_lotes_exportacion'))
    )
    op.create_table('solicitudes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tipo', sa.Enum('retiro_ingreso', 'licencia_especial', 'franco_compensatorio', 'franco_autorizado', 'cambio_turno', name='tipo', native_enum=False, create_constraint=True, length=30), nullable=False),
    sa.Column('estado', sa.Enum('BORRADOR', 'PENDIENTE_COMPANERO', 'PENDIENTE_JEFE', 'PENDIENTE_RRHH', 'APROBADA', 'EXPORTADA', 'CARGADA_GMS', 'ERROR_CARGA', 'RECHAZADA', 'CANCELADA', name='estado', native_enum=False, create_constraint=True, length=30), nullable=False),
    sa.Column('solicitante_legajo', sa.Integer(), nullable=False),
    sa.Column('solicitante_nombre', sa.String(length=120), nullable=False),
    sa.Column('jefe_legajo', sa.Integer(), nullable=True),
    sa.Column('jefe_nombre', sa.String(length=120), nullable=True),
    sa.Column('companero_legajo', sa.Integer(), nullable=True),
    sa.Column('companero_nombre', sa.String(length=120), nullable=True),
    sa.Column('datos', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('comentario', sa.String(length=500), nullable=True),
    sa.Column('advertencias', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('creada_en', sa.DateTime(timezone=True), nullable=False),
    sa.Column('enviada_en', sa.DateTime(timezone=True), nullable=True),
    sa.Column('lote_exportacion_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['lote_exportacion_id'], ['lotes_exportacion.id'], name=op.f('fk_solicitudes_lote_exportacion_id_lotes_exportacion')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_solicitudes'))
    )
    op.create_index(op.f('ix_solicitudes_companero_legajo'), 'solicitudes', ['companero_legajo'], unique=False)
    op.create_index(op.f('ix_solicitudes_estado'), 'solicitudes', ['estado'], unique=False)
    op.create_index(op.f('ix_solicitudes_jefe_legajo'), 'solicitudes', ['jefe_legajo'], unique=False)
    op.create_index(op.f('ix_solicitudes_solicitante_legajo'), 'solicitudes', ['solicitante_legajo'], unique=False)
    op.create_table('auditoria',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('solicitud_id', sa.Integer(), nullable=False),
    sa.Column('usuario_legajo', sa.Integer(), nullable=False),
    sa.Column('usuario_nombre', sa.String(length=120), nullable=False),
    sa.Column('rol', sa.String(length=20), nullable=False),
    sa.Column('accion', sa.String(length=30), nullable=False),
    sa.Column('estado_anterior', sa.Enum('BORRADOR', 'PENDIENTE_COMPANERO', 'PENDIENTE_JEFE', 'PENDIENTE_RRHH', 'APROBADA', 'EXPORTADA', 'CARGADA_GMS', 'ERROR_CARGA', 'RECHAZADA', 'CANCELADA', name='estado_anterior', native_enum=False, create_constraint=True, length=30), nullable=True),
    sa.Column('estado_nuevo', sa.Enum('BORRADOR', 'PENDIENTE_COMPANERO', 'PENDIENTE_JEFE', 'PENDIENTE_RRHH', 'APROBADA', 'EXPORTADA', 'CARGADA_GMS', 'ERROR_CARGA', 'RECHAZADA', 'CANCELADA', name='estado_nuevo', native_enum=False, create_constraint=True, length=30), nullable=False),
    sa.Column('motivo', sa.Text(), nullable=True),
    sa.Column('detalle', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['solicitud_id'], ['solicitudes.id'], name=op.f('fk_auditoria_solicitud_id_solicitudes')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_auditoria'))
    )
    op.create_index(op.f('ix_auditoria_solicitud_id'), 'auditoria', ['solicitud_id'], unique=False)
    op.create_table('novedades',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('lote_id', sa.Integer(), nullable=False),
    sa.Column('solicitud_id', sa.Integer(), nullable=False),
    sa.Column('orden', sa.Integer(), nullable=False),
    sa.Column('legajo', sa.Integer(), nullable=False),
    sa.Column('concepto', sa.Integer(), nullable=False),
    sa.Column('cantidad', sa.Integer(), nullable=False),
    sa.Column('fecha_desde', sa.Date(), nullable=False),
    sa.Column('fecha_hasta', sa.Date(), nullable=False),
    sa.Column('observaciones', sa.String(length=250), nullable=True),
    sa.Column('anio_novedad', sa.Integer(), nullable=False),
    sa.Column('mes_novedad', sa.Integer(), nullable=False),
    sa.Column('fecha_validar_fichadas', sa.Date(), nullable=True),
    sa.Column('fecha_nov28', sa.Date(), nullable=True),
    sa.Column('hora_desde', sa.String(length=5), nullable=True),
    sa.Column('hora_hasta', sa.String(length=5), nullable=True),
    sa.Column('codigo_futuro', sa.Integer(), nullable=True),
    sa.Column('advertencias', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.ForeignKeyConstraint(['lote_id'], ['lotes_exportacion.id'], name=op.f('fk_novedades_lote_id_lotes_exportacion')),
    sa.ForeignKeyConstraint(['solicitud_id'], ['solicitudes.id'], name=op.f('fk_novedades_solicitud_id_solicitudes')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_novedades'))
    )
    op.create_index(op.f('ix_novedades_lote_id'), 'novedades', ['lote_id'], unique=False)
    op.create_index(op.f('ix_novedades_solicitud_id'), 'novedades', ['solicitud_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_novedades_solicitud_id'), table_name='novedades')
    op.drop_index(op.f('ix_novedades_lote_id'), table_name='novedades')
    op.drop_table('novedades')
    op.drop_index(op.f('ix_auditoria_solicitud_id'), table_name='auditoria')
    op.drop_table('auditoria')
    op.drop_index(op.f('ix_solicitudes_solicitante_legajo'), table_name='solicitudes')
    op.drop_index(op.f('ix_solicitudes_jefe_legajo'), table_name='solicitudes')
    op.drop_index(op.f('ix_solicitudes_estado'), table_name='solicitudes')
    op.drop_index(op.f('ix_solicitudes_companero_legajo'), table_name='solicitudes')
    op.drop_table('solicitudes')
    op.drop_table('lotes_exportacion')
