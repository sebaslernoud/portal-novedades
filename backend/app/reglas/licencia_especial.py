"""Licencia especial → 41, con CODIGOFUTURO según el tipo.

Original: proyecto-auto-sc/src/reglas/licenciaEspecial.js. No hay controles sobre el
reintegro (pedido de RR.HH.).
"""

from datetime import date, timedelta

from app.reglas import motivos as m
from app.reglas.coherencia import control_tope_legal, controles_periodo
from app.reglas.comunes import asignar_persona, finalizar
from app.reglas.constantes import (
    CODIGO_FUTURO_LICENCIA,
    LICENCIAS_SIN_C9,
    TIPOS_LICENCIA_LEGIBLES,
    TOPES_LEGALES_LICENCIA,
)
from app.reglas.entradas import LicenciaEspecial
from app.reglas.fechas import dias_inclusivos, formatear
from app.reglas.fila import FilaNovedad, agregar_motivos, crear_fila


def regla_licencia_especial(solicitud: LicenciaEspecial, hoy: date) -> list[FilaNovedad]:
    fila = crear_fila(hoy, concepto=41)
    asignar_persona(fila, solicitud.persona)

    fila.fecha_desde = solicitud.fecha_desde
    if solicitud.fecha_hasta:
        fila.fecha_hasta = solicitud.fecha_hasta
    elif solicitud.fecha_reintegro:
        fila.fecha_hasta = solicitud.fecha_reintegro - timedelta(days=1)
        agregar_motivos(fila, m.hasta_deducida_de_reintegro(formatear(solicitud.fecha_reintegro)))

    if fila.fecha_desde and fila.fecha_hasta and fila.fecha_hasta >= fila.fecha_desde:
        fila.cantidad = dias_inclusivos(fila.fecha_desde, fila.fecha_hasta)

    tipo = solicitud.tipo_licencia or ""
    tipo_legible = TIPOS_LICENCIA_LEGIBLES.get(tipo)
    if tipo_legible:
        fila.observaciones = f"Licencia especial: {tipo_legible}"
    else:
        fila.observaciones = (
            f"Licencia especial: {solicitud.motivo}" if solicitud.motivo else "Licencia especial"
        )
        agregar_motivos(fila, m.LICENCIA_NO_IDENTIFICADA)

    fila.codigo_futuro = CODIGO_FUTURO_LICENCIA.get(tipo)
    if fila.codigo_futuro is None:
        agregar_motivos(fila, m.COMPLETAR_CODIGO_FUTURO)

    motivos_formulario = [
        *controles_periodo(
            fila.fecha_desde,
            fila.fecha_hasta,
            hoy,
            cantidad_escrita=solicitud.cantidad_dias,
            omitir_c9=tipo in LICENCIAS_SIN_C9,
        ),
        *control_tope_legal(
            TOPES_LEGALES_LICENCIA.get(tipo), tipo_legible, fila.cantidad, solicitud.cantidad_dias
        ),
    ]
    return finalizar([fila], motivos_formulario)
