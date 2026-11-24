"""Advertencias que ven los aprobadores. No bloquean el envío.

Son los motivos del motor heredado más los que agrega la especificación del portal:
GEN-1 (fecha a más de 1 año de hoy) y RI-4 (retiro o ingreso sin devoluciones).
"""

from datetime import date

from app.reglas import generar_filas
from app.reglas import motivos as m
from app.reglas.entradas import (
    CambioTurno,
    FrancoAutorizado,
    FrancoCompensatorio,
    LicenciaEspecial,
    RetiroIngreso,
    Solicitud,
    Vacaciones,
)
from app.reglas.fila import FilaNovedad

DIAS_GEN_1 = 365


def _fechas(solicitud: Solicitud) -> list[date | None]:
    match solicitud:
        case RetiroIngreso():
            return [solicitud.fecha, *(r.fecha for r in solicitud.devoluciones)]
        case LicenciaEspecial() | Vacaciones():
            return [solicitud.fecha_desde, solicitud.fecha_hasta, solicitud.fecha_reintegro]
        case FrancoCompensatorio():
            return [solicitud.fecha_franco, *(r.fecha for r in solicitud.dias_trabajados)]
        case FrancoAutorizado():
            return [solicitud.fecha_franco]
        case CambioTurno():
            return [solicitud.fecha_cambio, solicitud.fecha_devolucion]
    return []


def advertencias_de_filas(filas: list[FilaNovedad]) -> list[str]:
    resultado: list[str] = []
    for fila in filas:
        resultado.extend(motivo for motivo in fila.motivos if motivo not in resultado)
    return resultado


def calcular_advertencias(solicitud: Solicitud, hoy: date) -> list[str]:
    advertencias = advertencias_de_filas(generar_filas(solicitud, hoy))
    lejanas = sorted({f for f in _fechas(solicitud) if f and abs((f - hoy).days) > DIAS_GEN_1})
    advertencias.extend(m.fecha_lejana(f) for f in lejanas)
    if isinstance(solicitud, RetiroIngreso) and not solicitud.devoluciones:
        advertencias.append(m.SIN_DEVOLUCIONES)
    return advertencias
