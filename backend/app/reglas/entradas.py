"""Datos de una solicitud aprobada, ya tipados, tal como los recibe el motor de reglas.

Fechas como `date`, horas como "HH:MM" y legajos como `int`. Los campos opcionales del
formulario llegan como None.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Literal


@dataclass(frozen=True)
class Persona:
    legajo: int | None
    nombre: str | None = None


@dataclass(frozen=True)
class Renglon:
    """Renglón de devolución de horas o de día trabajado."""

    fecha: date | None
    hora_desde: str | None
    hora_hasta: str | None

    def tiene_datos(self) -> bool:
        return bool(self.fecha or self.hora_desde or self.hora_hasta)


@dataclass(frozen=True)
class RetiroIngreso:
    persona: Persona | None
    tipo: Literal["retiro", "ingreso"]
    fecha: date | None
    hora: str | None
    horario_laboral_desde: str | None
    horario_laboral_hasta: str | None
    motivo: str | None = None
    devoluciones: list[Renglon] = field(default_factory=list)


@dataclass(frozen=True)
class LicenciaEspecial:
    persona: Persona | None
    tipo_licencia: str | None
    fecha_desde: date | None
    fecha_hasta: date | None
    fecha_reintegro: date | None = None
    cantidad_dias: int | None = None
    motivo: str | None = None


@dataclass(frozen=True)
class FrancoCompensatorio:
    persona: Persona | None
    fecha_franco: date | None
    hora_desde_franco: str | None
    hora_hasta_franco: str | None
    # Se guarda pero no cambia las filas.
    franco_a_determinar: bool = False
    dias_trabajados: list[Renglon] = field(default_factory=list)
    motivo: str | None = None


@dataclass(frozen=True)
class FrancoAutorizado:
    persona: Persona | None
    fecha_franco: date | None
    motivo: str | None = None


@dataclass(frozen=True)
class CambioTurno:
    """Con una sola persona con datos se trata como cambio de horario (22)."""

    solicitante: Persona | None
    aceptante: Persona | None
    fecha_cambio: date | None
    fecha_devolucion: date | None


@dataclass(frozen=True)
class Vacaciones:
    persona: Persona | None
    fecha_desde: date | None
    fecha_hasta: date | None
    fecha_reintegro: date | None = None
    cantidad_dias: int | None = None


Solicitud = (
    RetiroIngreso | LicenciaEspecial | FrancoCompensatorio | FrancoAutorizado | CambioTurno | Vacaciones
)
