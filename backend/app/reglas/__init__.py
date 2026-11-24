"""Motor de reglas: convierte una solicitud aprobada en filas de novedades para GMS.

Es un port fiel de proyecto-auto-sc (docs/REGLAS-DE-NEGOCIO.md) y se valida contra
docs/casos-de-prueba-reglas.json en tests/test_reglas_heredadas.py.
"""

from datetime import date

from app.reglas.cambio_turno import regla_cambio_turno
from app.reglas.entradas import (
    CambioTurno,
    FrancoAutorizado,
    FrancoCompensatorio,
    LicenciaEspecial,
    RetiroIngreso,
    Solicitud,
    Vacaciones,
)
from app.reglas.fechas import hoy_negocio
from app.reglas.fila import FilaNovedad
from app.reglas.franco_autorizado import regla_franco_autorizado
from app.reglas.franco_compensatorio import regla_franco_compensatorio
from app.reglas.licencia_especial import regla_licencia_especial
from app.reglas.retiro_ingreso import regla_retiro_ingreso
from app.reglas.vacaciones import regla_vacaciones


def generar_filas(solicitud: Solicitud, hoy: date | None = None) -> list[FilaNovedad]:
    """`hoy` define AnioNovedad/mesNovedad y los controles de fechas; por defecto, hoy en Buenos Aires."""
    hoy = hoy or hoy_negocio()
    match solicitud:
        case RetiroIngreso():
            return regla_retiro_ingreso(solicitud, hoy)
        case LicenciaEspecial():
            return regla_licencia_especial(solicitud, hoy)
        case FrancoCompensatorio():
            return regla_franco_compensatorio(solicitud, hoy)
        case FrancoAutorizado():
            return regla_franco_autorizado(solicitud, hoy)
        case CambioTurno():
            return regla_cambio_turno(solicitud, hoy)
        case Vacaciones():
            return regla_vacaciones(solicitud, hoy)
    raise TypeError(f"Tipo de solicitud desconocido: {type(solicitud).__name__}")


__all__ = ["FilaNovedad", "generar_filas"]
