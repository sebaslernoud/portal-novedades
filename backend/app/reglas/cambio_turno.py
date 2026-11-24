"""Cambio de turno → dos filas 37; con una sola persona, cambio de horario → una fila 22.

Original: proyecto-auto-sc/src/reglas/cambioTurno.js. Cada persona tiene un 37 el día que
trabaja por la otra y, en FechaNov28, el día en que se devuelve el cambio.
"""

from datetime import date

from app.reglas import motivos as m
from app.reglas.coherencia import control_misma_persona
from app.reglas.comunes import asignar_persona, finalizar
from app.reglas.entradas import CambioTurno, Persona
from app.reglas.fechas import formatear
from app.reglas.fila import FilaNovedad, agregar_motivos, crear_fila
from app.reglas.textos import unir_partes


def observacion_cambio(
    propio: str | None, otro: str | None, dia_cambio: date | None, dia_devolucion: date | None
) -> str:
    """Ej.: "JUAN PEREZ x ANA GOMEZ - Día del Cambio: 06/12/2026 - Día de devolución: 10/12/2026"."""
    sin_nombre = "(sin nombre)"
    return unir_partes(
        [
            f"{propio if propio is not None else sin_nombre} x {otro if otro is not None else sin_nombre}",
            f"Día del Cambio: {formatear(dia_cambio)}" if dia_cambio else None,
            f"Día de devolución: {formatear(dia_devolucion)}" if dia_devolucion else None,
        ],
        " - ",
    )


def _tiene_datos(persona: Persona | None) -> bool:
    if persona is None:
        return False
    return persona.legajo is not None or bool(persona.nombre and persona.nombre.strip())


def _regla_cambio_horario(solicitud: CambioTurno, persona: Persona | None, hoy: date) -> list[FilaNovedad]:
    cambio = solicitud.fecha_cambio
    devolucion = solicitud.fecha_devolucion
    fila = crear_fila(hoy, concepto=22, cantidad=1)
    asignar_persona(fila, persona)
    fila.fecha_desde = cambio
    fila.fecha_hasta = cambio
    fila.observaciones = f"Cambio de horario el {formatear(cambio)}." if cambio else "Cambio de horario."
    if cambio and devolucion and devolucion != cambio:
        agregar_motivos(fila, m.cambio_horario_fechas_distintas(formatear(cambio), formatear(devolucion)))
    return finalizar([fila])


def regla_cambio_turno(solicitud: CambioTurno, hoy: date) -> list[FilaNovedad]:
    solicitante = solicitud.solicitante
    aceptante = solicitud.aceptante
    if _tiene_datos(solicitante) != _tiene_datos(aceptante):
        return _regla_cambio_horario(solicitud, solicitante if _tiene_datos(solicitante) else aceptante, hoy)

    cambio = solicitud.fecha_cambio
    devolucion = solicitud.fecha_devolucion
    definicion = [
        (solicitante, aceptante, "solicitante", cambio, devolucion),
        (aceptante, solicitante, "aceptante", devolucion, cambio),
    ]
    filas = []
    for persona, otra, rol, fecha, devuelve in definicion:
        fila = crear_fila(hoy, concepto=37, cantidad=1)
        if persona:
            asignar_persona(fila, persona)
        else:
            agregar_motivos(fila, m.falta_identificar(rol))
        fila.fecha_desde = fecha
        fila.fecha_hasta = fecha
        fila.fecha_nov28 = devuelve
        fila.observaciones = observacion_cambio(
            persona.nombre if persona else None, otra.nombre if otra else None, fecha, devuelve
        )
        filas.append(fila)

    return finalizar(filas, control_misma_persona(solicitante, aceptante), agrupar=True)
