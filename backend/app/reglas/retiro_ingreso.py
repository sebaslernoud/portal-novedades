"""Retiro / ingreso fuera de horario → 26 o 42, más una 28 por renglón de devolución.

Original: proyecto-auto-sc/src/reglas/retiroIngreso.js. El horario laboral solo se usa para
verificar que las horas cierren (C12): no va al Excel.
"""

from datetime import date

from app.reglas import motivos as m
from app.reglas.coherencia import (
    Tramo,
    control_devolucion_anterior,
    control_horas_devolucion,
    separar_excedente,
)
from app.reglas.comunes import asignar_persona, filas_por_tramos, finalizar
from app.reglas.constantes import MAX_RENGLONES_DEVOLUCION
from app.reglas.entradas import RetiroIngreso
from app.reglas.fechas import formatear
from app.reglas.fila import FilaNovedad, agregar_motivos, crear_fila
from app.reglas.horas import formatear_duracion
from app.reglas.textos import lista_dias, unir_partes


def _texto_ausencia(codigo: int, solicitud: RetiroIngreso) -> str | None:
    """Retiro: de la hora al fin del turno. Ingreso: del inicio del turno a la hora."""
    if not solicitud.fecha:
        return None
    hora = solicitud.hora
    rango = None
    if hora:
        if codigo == 42:
            desde = solicitud.horario_laboral_desde
            rango = f"{desde}-{hora} hs" if desde else f"hasta las {hora} hs"
        else:
            hasta = solicitud.horario_laboral_hasta
            rango = f"{hora}-{hasta} hs" if hasta else f"desde las {hora} hs"
    return unir_partes(["No trabajó el", formatear(solicitud.fecha), rango]) + "."


def regla_retiro_ingreso(solicitud: RetiroIngreso, hoy: date) -> list[FilaNovedad]:
    codigo = 42 if solicitud.tipo == "ingreso" else 26
    motivos_formulario: list[str] = []

    principal = crear_fila(hoy, concepto=codigo, cantidad=1)
    asignar_persona(principal, solicitud.persona)
    principal.fecha_desde = solicitud.fecha
    principal.fecha_hasta = solicitud.fecha
    etiqueta = "Ingreso" if codigo == 42 else "Retiro"
    encabezado = f"{etiqueta} {solicitud.hora} hs." if solicitud.hora else f"{etiqueta}."
    ausencia = _texto_ausencia(codigo, solicitud)

    renglones = [r for r in solicitud.devoluciones if r.tiene_datos()]
    if len(renglones) > MAX_RENGLONES_DEVOLUCION:
        motivos_formulario.append(m.mas_renglones(len(renglones), MAX_RENGLONES_DEVOLUCION))

    filas_devolucion: list[FilaNovedad] = []
    for renglon in renglones:
        fila = crear_fila(hoy, concepto=28, cantidad=1)
        asignar_persona(fila, solicitud.persona)
        fila.fecha_desde = renglon.fecha
        fila.fecha_hasta = renglon.fecha
        fila.hora_desde = renglon.hora_desde
        fila.hora_hasta = renglon.hora_hasta
        if renglon.hora_hasta is None:
            agregar_motivos(fila, m.COMPLETAR_HORA_HASTA)
        fila.observaciones = unir_partes(["Devolución de horas.", ausencia])
        agregar_motivos(fila, control_devolucion_anterior(solicitud.fecha, renglon.fecha))
        filas_devolucion.append(fila)

    filas_28 = filas_devolucion
    if filas_devolucion:
        control = control_horas_devolucion(
            codigo,
            solicitud.hora,
            solicitud.horario_laboral_desde,
            solicitud.horario_laboral_hasta,
            [(f.hora_desde, f.hora_hasta) for f in filas_devolucion],
        )
        agregar_motivos(principal, control.motivos_principal)
        motivos_devoluciones = control.motivos_devoluciones

        # Si devuelve de más, el excedente va a una 28 aparte y el resto cierra justo.
        if (
            control.adeudado is not None
            and control.devuelto is not None
            and control.devuelto > control.adeudado
        ):
            separacion = separar_excedente(
                [Tramo(i, f.fecha_desde, f.hora_desde, f.hora_hasta) for i, f in enumerate(filas_devolucion)],
                control.adeudado,
            )
            if separacion:
                tramos, minutos_a_favor = separacion
                a_favor = formatear_duracion(minutos_a_favor)
                origen = "del ingreso" if codigo == 42 else "del retiro"
                if principal.fecha_desde:
                    origen += f" del {formatear(principal.fecha_desde)}"

                def armar_a_favor(fila: FilaNovedad) -> None:
                    fecha = formatear(fila.fecha_desde) if fila.fecha_desde else ""
                    fila.observaciones = (
                        f"Horas a favor el {fecha} de {fila.hora_desde} a {fila.hora_hasta} hs, "
                        f"excedente de la devolución {origen}."
                    )
                    agregar_motivos(fila, m.horas_a_favor(a_favor))

                filas_28 = filas_por_tramos(filas_devolucion, tramos, armar_a_favor)
                motivos_devoluciones = []

        for fila in filas_28:
            agregar_motivos(fila, motivos_devoluciones)

    dias = lista_dias(f.fecha_desde for f in filas_28 if not f.a_favor)
    principal.observaciones = unir_partes(
        [encabezado, f"Devuelve {dias}." if dias else None, solicitud.motivo]
    )

    return finalizar([principal, *filas_28], motivos_formulario)
