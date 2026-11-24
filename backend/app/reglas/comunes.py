"""Pasos compartidos por todas las reglas: legajo, obligatorios, cierre del formulario y tramos."""

from collections.abc import Callable
from dataclasses import replace

from app.reglas import motivos as m
from app.reglas.coherencia import Tramo
from app.reglas.constantes import OBSERVACIONES_MAX_CARACTERES
from app.reglas.entradas import Persona
from app.reglas.fila import FilaNovedad, agregar_motivos
from app.reglas.textos import normalizar_observaciones


def asignar_persona(fila: FilaNovedad, persona: Persona | None) -> None:
    fila.legajo = persona.legajo if persona else None
    if fila.legajo is None:
        agregar_motivos(fila, m.FALTA_LEGAJO)


def verificar_obligatorios(fila: FilaNovedad) -> None:
    if fila.legajo is None:
        agregar_motivos(fila, m.FALTA_LEGAJO)
    if fila.concepto is None:
        agregar_motivos(fila, m.falta("Concepto"))
    if fila.cantidad is None:
        agregar_motivos(fila, m.falta("Cantidad"))
    if fila.fecha_desde is None:
        agregar_motivos(fila, m.falta("FechaDesde"))
    if fila.fecha_hasta is None:
        agregar_motivos(fila, m.falta("FechaHasta"))
    if fila.concepto == 28 and fila.hora_desde is None:
        agregar_motivos(fila, m.falta("HORADESDE"))
    if fila.concepto == 37 and fila.fecha_nov28 is None:
        agregar_motivos(fila, m.falta("FechaNov28"))


def finalizar(
    filas: list[FilaNovedad], motivos_formulario: list[str] | None = None, agrupar: bool = False
) -> list[FilaNovedad]:
    """Obligatorios → motivos comunes → Observaciones normalizadas → tope de 250 caracteres."""
    for fila in filas:
        verificar_obligatorios(fila)
        agregar_motivos(fila, motivos_formulario or [])
        fila.observaciones = normalizar_observaciones(fila.observaciones)
        largo = len(fila.observaciones or "")
        if largo > OBSERVACIONES_MAX_CARACTERES:
            agregar_motivos(fila, m.observaciones_largas(largo))
    # Las filas de un mismo cambio de turno se revisan siempre juntas.
    if agrupar and any(f.motivos for f in filas):
        for fila in filas:
            if not fila.motivos:
                agregar_motivos(fila, m.GRUPO_CAMBIO_TURNO)
    return filas


def filas_por_tramos(
    filas_base: list[FilaNovedad], tramos: list[Tramo], armar_a_favor: Callable[[FilaNovedad], None]
) -> list[FilaNovedad]:
    """Una fila 28 por tramo, copiando la de su renglón con las fechas y horas del tramo."""
    filas = []
    for tramo in tramos:
        base = filas_base[tramo.indice]
        fila = replace(
            base,
            motivos=list(base.motivos),
            fecha_desde=tramo.fecha,
            fecha_hasta=tramo.fecha,
            hora_desde=tramo.hora_desde,
            hora_hasta=tramo.hora_hasta,
            fecha_validar_fichadas=tramo.fecha if base.fecha_validar_fichadas else None,
        )
        if tramo.a_favor:
            fila.a_favor = True
            armar_a_favor(fila)
        filas.append(fila)
    return filas
