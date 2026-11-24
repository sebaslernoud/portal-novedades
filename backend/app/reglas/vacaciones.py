"""Vacaciones → 2. Fuera del alcance inicial del portal; se porta porque tiene caso de prueba.

Original: proyecto-auto-sc/src/reglas/vacaciones.js.
"""

from datetime import date, timedelta

from app.reglas import motivos as m
from app.reglas.coherencia import controles_periodo
from app.reglas.comunes import asignar_persona, finalizar
from app.reglas.entradas import Vacaciones
from app.reglas.fechas import dias_inclusivos, formatear
from app.reglas.fila import FilaNovedad, agregar_motivos, crear_fila


def regla_vacaciones(solicitud: Vacaciones, hoy: date) -> list[FilaNovedad]:
    fila = crear_fila(hoy, concepto=2)
    asignar_persona(fila, solicitud.persona)

    fila.fecha_desde = solicitud.fecha_desde
    if solicitud.fecha_hasta:
        fila.fecha_hasta = solicitud.fecha_hasta
    elif solicitud.fecha_reintegro:
        fila.fecha_hasta = solicitud.fecha_reintegro - timedelta(days=1)
        agregar_motivos(fila, m.hasta_deducida_de_reintegro(formatear(solicitud.fecha_reintegro)))

    if solicitud.cantidad_dias is not None:
        fila.cantidad = solicitud.cantidad_dias
    elif fila.fecha_desde and fila.fecha_hasta and fila.fecha_hasta >= fila.fecha_desde:
        fila.cantidad = dias_inclusivos(fila.fecha_desde, fila.fecha_hasta)
        agregar_motivos(fila, m.cantidad_calculada(fila.cantidad))

    motivos_formulario = controles_periodo(
        fila.fecha_desde, fila.fecha_hasta, hoy, cantidad_escrita=solicitud.cantidad_dias
    )
    return finalizar([fila], motivos_formulario)
