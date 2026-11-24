"""Solicitudes de novedades, su auditoría y las exportaciones a GMS."""

from datetime import date, datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class TipoSolicitud(StrEnum):
    RETIRO_INGRESO = "retiro_ingreso"
    LICENCIA_ESPECIAL = "licencia_especial"
    FRANCO_COMPENSATORIO = "franco_compensatorio"
    FRANCO_AUTORIZADO = "franco_autorizado"
    CAMBIO_TURNO = "cambio_turno"


class EstadoSolicitud(StrEnum):
    """Estados de la especificación (§3.1) más EXPORTADA (Excel generado para GMS)."""

    BORRADOR = "BORRADOR"
    PENDIENTE_COMPANERO = "PENDIENTE_COMPANERO"
    PENDIENTE_JEFE = "PENDIENTE_JEFE"
    PENDIENTE_RRHH = "PENDIENTE_RRHH"
    APROBADA = "APROBADA"
    EXPORTADA = "EXPORTADA"
    CARGADA_GMS = "CARGADA_GMS"
    ERROR_CARGA = "ERROR_CARGA"
    RECHAZADA = "RECHAZADA"
    CANCELADA = "CANCELADA"


def _enum(clase: type[StrEnum], nombre: str) -> Enum:
    # VARCHAR + CHECK en lugar de un tipo nativo: agregar un valor no exige alterar el tipo.
    return Enum(
        clase,
        name=nombre,
        native_enum=False,
        create_constraint=True,
        length=30,
        values_callable=lambda e: [m.value for m in e],
    )


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[TipoSolicitud] = mapped_column(_enum(TipoSolicitud, "tipo"))
    estado: Mapped[EstadoSolicitud] = mapped_column(_enum(EstadoSolicitud, "estado"), index=True)
    solicitante_legajo: Mapped[int] = mapped_column(Integer, index=True)
    solicitante_nombre: Mapped[str] = mapped_column(String(120))
    # En un borrador pueden faltar; se exigen al enviar.
    jefe_legajo: Mapped[int | None] = mapped_column(Integer, index=True)
    jefe_nombre: Mapped[str | None] = mapped_column(String(120))
    companero_legajo: Mapped[int | None] = mapped_column(Integer, index=True)
    companero_nombre: Mapped[str | None] = mapped_column(String(120))
    # Campos propios del formulario (fechas ISO, horas "HH:MM").
    datos: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    comentario: Mapped[str | None] = mapped_column(String(500))
    advertencias: Mapped[list[str]] = mapped_column(JSONB, default=list)
    creada_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    enviada_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    lote_exportacion_id: Mapped[int | None] = mapped_column(ForeignKey("lotes_exportacion.id"))

    auditoria: Mapped[list["RegistroAuditoria"]] = relationship(
        back_populates="solicitud", order_by="RegistroAuditoria.id"
    )


class RegistroAuditoria(Base):
    """Reemplaza a la firma en papel. Solo se insertan filas: nunca se modifican ni se borran."""

    __tablename__ = "auditoria"

    id: Mapped[int] = mapped_column(primary_key=True)
    solicitud_id: Mapped[int] = mapped_column(ForeignKey("solicitudes.id"), index=True)
    usuario_legajo: Mapped[int] = mapped_column(Integer)
    usuario_nombre: Mapped[str] = mapped_column(String(120))
    rol: Mapped[str] = mapped_column(String(20))
    accion: Mapped[str] = mapped_column(String(30))
    estado_anterior: Mapped[EstadoSolicitud | None] = mapped_column(_enum(EstadoSolicitud, "estado_anterior"))
    estado_nuevo: Mapped[EstadoSolicitud] = mapped_column(_enum(EstadoSolicitud, "estado_nuevo"))
    motivo: Mapped[str | None] = mapped_column(Text)
    detalle: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    solicitud: Mapped[Solicitud] = relationship(back_populates="auditoria")


class LoteExportacion(Base):
    __tablename__ = "lotes_exportacion"

    id: Mapped[int] = mapped_column(primary_key=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    usuario_legajo: Mapped[int] = mapped_column(Integer)
    usuario_nombre: Mapped[str] = mapped_column(String(120))
    nombre_archivo: Mapped[str] = mapped_column(String(120))
    anio_novedad: Mapped[int] = mapped_column(Integer)
    mes_novedad: Mapped[int] = mapped_column(Integer)
    cantidad_filas: Mapped[int] = mapped_column(Integer)

    novedades: Mapped[list["Novedad"]] = relationship(back_populates="lote", order_by="Novedad.orden")
    solicitudes: Mapped[list[Solicitud]] = relationship()


class Novedad(Base):
    """Foto de cada fila exportada: con esto el mismo Excel se puede volver a bajar idéntico."""

    __tablename__ = "novedades"

    id: Mapped[int] = mapped_column(primary_key=True)
    lote_id: Mapped[int] = mapped_column(ForeignKey("lotes_exportacion.id"), index=True)
    solicitud_id: Mapped[int] = mapped_column(ForeignKey("solicitudes.id"), index=True)
    orden: Mapped[int] = mapped_column(Integer)
    legajo: Mapped[int] = mapped_column(Integer)
    concepto: Mapped[int] = mapped_column(Integer)
    cantidad: Mapped[int] = mapped_column(Integer)
    fecha_desde: Mapped[date] = mapped_column(Date)
    fecha_hasta: Mapped[date] = mapped_column(Date)
    observaciones: Mapped[str | None] = mapped_column(String(250))
    anio_novedad: Mapped[int] = mapped_column(Integer)
    mes_novedad: Mapped[int] = mapped_column(Integer)
    fecha_validar_fichadas: Mapped[date | None] = mapped_column(Date)
    fecha_nov28: Mapped[date | None] = mapped_column(Date)
    hora_desde: Mapped[str | None] = mapped_column(String(5))
    hora_hasta: Mapped[str | None] = mapped_column(String(5))
    codigo_futuro: Mapped[int | None] = mapped_column(Integer)
    advertencias: Mapped[list[str]] = mapped_column(JSONB, default=list)

    lote: Mapped[LoteExportacion] = relationship(back_populates="novedades")
