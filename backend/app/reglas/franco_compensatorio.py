"""Franco compensatorio → 38 (día del franco) y una 28 por día trabajado.

Original: proyecto-auto-sc/src/reglas/francoCompensatorio.js.
  - franco + días trabajados → 38 + una 28 por renglón
  - solo franco              → solo 38
  - solo días trabajados     → solo las 28
"""

from datetime import date

from app.reglas import motivos as m
from app.reglas.coherencia import Tramo, control_mismo_dia_franco, separar_excedente
from app.reglas.comunes import asignar_persona, filas_por_tramos, finalizar
from app.reglas.constantes import MAX_RENGLONES_DEVOLUCION
from app.reglas.entradas import FrancoCompensatorio
from app.reglas.fechas import formatear
from app.reglas.fila import FilaNovedad, agregar_motivos, crear_fila
from app.reglas.horas import duracion_minutos, formatear_duracion
from app.reglas.textos import lista_dias, unir_partes


def _control_horas_franco(
    desde_franco: str | None, hasta_franco: str | None, renglones: list[tuple[str | None, str | None]]
) -> tuple[list[str], int | None, int | None]:
    """Horas del franco contra la suma de lo trabajado → (motivos, minutos franco, minutos trabajados)."""
    if any(desde is None or hasta is None for desde, hasta in renglones):
        return [], None, None
    if not desde_franco or not hasta_franco:
        return [m.NO_SE_PUDO_VERIFICAR_HORAS_FRANCO], None, None
    franco = duracion_minutos(desde_franco, hasta_franco)
    trabajado = sum(duracion_minutos(desde, hasta) for desde, hasta in renglones if desde and hasta)
    if franco == trabajado:
        return [], franco, trabajado
    return [m.c12_franco(formatear_duracion(franco), formatear_duracion(trabajado))], franco, trabajado


def _horario_trabajado(desde: str | None, hasta: str | None) -> str | None:
    if desde and hasta:
        return f"de {desde} a {hasta} hs"
    if desde:
        return f"desde las {desde} hs"
    if hasta:
        return f"hasta las {hasta} hs"
    return None


def regla_franco_compensatorio(solicitud: FrancoCompensatorio, hoy: date) -> list[FilaNovedad]:
    fecha_franco = solicitud.fecha_franco
    renglones = [r for r in solicitud.dias_trabajados if r.tiene_datos()]

    if not fecha_franco and not renglones:
        fila = crear_fila(hoy, concepto=38, cantidad=1)
        asignar_persona(fila, solicitud.persona)
        agregar_motivos(fila, m.FRANCO_SIN_FECHAS)
        fila.observaciones = unir_partes(["Franco compensatorio.", solicitud.motivo])
        return finalizar([fila])

    motivos_formulario: list[str] = []
    if len(renglones) > MAX_RENGLONES_DEVOLUCION:
        motivos_formulario.append(m.mas_renglones(len(renglones), MAX_RENGLONES_DEVOLUCION))

    hd_franco = solicitud.hora_desde_franco
    hh_franco = solicitud.hora_hasta_franco
    rango_franco = f"{hd_franco or '?'}-{hh_franco or '?'} hs" if hd_franco or hh_franco else None
    ausencia = (
        unir_partes(["No trabajó el", formatear(fecha_franco), rango_franco]) + "." if fecha_franco else None
    )

    def observacion_trabajo(fila: FilaNovedad) -> str:
        trabajo = unir_partes(
            [
                "Devolución de horas por tareas adicionales",
                f"el {formatear(fila.fecha_desde)}" if fila.fecha_desde else None,
                _horario_trabajado(fila.hora_desde, fila.hora_hasta),
            ]
        )
        return unir_partes([trabajo + ".", ausencia, solicitud.motivo])

    filas_trabajo: list[FilaNovedad] = []
    for renglon in renglones:
        fila = crear_fila(hoy, concepto=28, cantidad=1)
        asignar_persona(fila, solicitud.persona)
        fila.fecha_desde = renglon.fecha
        fila.fecha_hasta = renglon.fecha
        fila.hora_desde = renglon.hora_desde
        fila.hora_hasta = renglon.hora_hasta
        if renglon.hora_hasta is None:
            agregar_motivos(fila, m.FALTA_HORA_HASTA)
        # Las fichadas solo se pueden validar sobre un día que ya pasó.
        if renglon.fecha:
            if renglon.fecha <= hoy:
                fila.fecha_validar_fichadas = renglon.fecha
            else:
                agregar_motivos(fila, m.COMPLETAR_FICHADA_FRANCO)
        fila.observaciones = observacion_trabajo(fila)
        filas_trabajo.append(fila)

    motivos_horas: list[str] = []
    if fecha_franco and filas_trabajo:
        motivos_horas, franco, trabajado = _control_horas_franco(
            hd_franco, hh_franco, [(f.hora_desde, f.hora_hasta) for f in filas_trabajo]
        )
        # Si trabajó de más, el excedente va a una 28 aparte y el resto cierra justo.
        if franco is not None and trabajado is not None and trabajado > franco:
            separacion = separar_excedente(
                [Tramo(i, f.fecha_desde, f.hora_desde, f.hora_hasta) for i, f in enumerate(filas_trabajo)],
                franco,
            )
            if separacion:
                tramos, minutos_a_favor = separacion
                motivo_a_favor = m.horas_a_favor_franco(formatear_duracion(minutos_a_favor))
                filas_trabajo = filas_por_tramos(
                    filas_trabajo, tramos, lambda fila: agregar_motivos(fila, motivo_a_favor)
                )
                for fila in filas_trabajo:
                    if fila.a_favor and fila.fecha_desde:
                        fila.observaciones = (
                            f"Horas a favor el {formatear(fila.fecha_desde)} de {fila.hora_desde} a "
                            f"{fila.hora_hasta} hs, excedente de lo trabajado para el franco del "
                            f"{formatear(fecha_franco)}."
                        )
                    else:
                        fila.observaciones = observacion_trabajo(fila)
                motivos_horas = []

    filas: list[FilaNovedad] = []
    if fecha_franco:
        fila = crear_fila(hoy, concepto=38, cantidad=1)
        asignar_persona(fila, solicitud.persona)
        fila.fecha_desde = fecha_franco
        fila.fecha_hasta = fecha_franco
        dias = lista_dias(f.fecha_desde for f in filas_trabajo if not f.a_favor)
        fila.observaciones = unir_partes(
            [
                unir_partes(["Franco compensatorio", rango_franco]) + ".",
                f"Compensa lo trabajado {dias}." if dias else None,
                solicitud.motivo,
            ]
        )
        filas.append(fila)

    for fila in filas_trabajo:
        agregar_motivos(fila, motivos_horas)
        motivos_formulario.extend(control_mismo_dia_franco(fila.fecha_desde, fecha_franco))
    filas.extend(filas_trabajo)

    return finalizar(filas, motivos_formulario)
