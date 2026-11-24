"""Validación de cada fila antes de exportar (proyecto-auto-sc/src/http/excelRoute.js).

Una fila que no pasa la validación no se exporta. Las advertencias (`motivos`) no bloquean:
para cuando se exporta, RR.HH. ya las revisó en el circuito.
"""

import re
from collections.abc import Sequence
from dataclasses import dataclass, replace

from app.reglas.comunes import verificar_obligatorios
from app.reglas.constantes import CODIGOS_NOVEDAD, OBSERVACIONES_MAX_CARACTERES
from app.reglas.fila import FilaNovedad

_HORA = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")

# campo, mínimo, máximo, mensaje
_RANGOS: list[tuple[str, int, int, str]] = [
    ("legajo", 1, 99_999_999, "El legajo tiene que ser un número entero"),
    ("cantidad", 1, 999, "La cantidad tiene que ser un número entero entre 1 y 999"),
    ("anio_novedad", 2000, 2100, "Año de novedad inválido"),
    ("mes_novedad", 1, 12, "El mes de novedad tiene que estar entre 1 y 12"),
    ("codigo_futuro", 1, 9999, "El código futuro tiene que ser un número entero"),
]


@dataclass(frozen=True)
class ErrorValidacion:
    indice: int
    campo: str | None
    mensaje: str


def validar_fila(fila: FilaNovedad, indice: int = 0) -> list[ErrorValidacion]:
    errores: list[ErrorValidacion] = []

    def error(campo: str | None, mensaje: str) -> None:
        errores.append(ErrorValidacion(indice, campo, mensaje))

    for campo, minimo, maximo, mensaje in _RANGOS:
        valor = getattr(fila, campo)
        if valor is not None and not (isinstance(valor, int) and minimo <= valor <= maximo):
            error(campo, mensaje)

    if fila.concepto is not None and fila.concepto not in CODIGOS_NOVEDAD:
        error("concepto", f"El código {fila.concepto} no está en la tabla de códigos")

    for campo in ("hora_desde", "hora_hasta"):
        valor = getattr(fila, campo)
        if valor is not None and not _HORA.match(valor):
            error(campo, "Hora inválida: usar HH:MM")

    largo = len(fila.observaciones or "")
    if largo > OBSERVACIONES_MAX_CARACTERES:
        error(
            "observaciones",
            f"Las observaciones tienen {largo} caracteres y el máximo es {OBSERVACIONES_MAX_CARACTERES}: "
            "acortarlas",
        )

    control = replace(fila, motivos=[])
    verificar_obligatorios(control)
    for motivo in control.motivos:
        error(None, motivo)
    return errores


def separar_validas(
    filas: Sequence[FilaNovedad],
) -> tuple[list[FilaNovedad], list[ErrorValidacion]]:
    """Devuelve las filas exportables y los errores de las que no lo son."""
    validas: list[FilaNovedad] = []
    errores: list[ErrorValidacion] = []
    for indice, fila in enumerate(filas):
        errores_fila = validar_fila(fila, indice)
        if errores_fila:
            errores.extend(errores_fila)
        else:
            validas.append(fila)
    return validas, errores
