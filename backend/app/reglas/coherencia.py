"""Controles de coherencia. Generan advertencias para los aprobadores: no bloquean el envío."""

from dataclasses import dataclass, field, replace
from datetime import date, timedelta

from app.reglas import motivos as m
from app.reglas.constantes import DIAS_MAX_ANTIGUEDAD, DIAS_MAX_PERIODO, TopeLegal
from app.reglas.entradas import Persona
from app.reglas.fechas import dias_inclusivos, diferencia_dias, formatear
from app.reglas.horas import duracion_minutos, formatear_duracion, minutos, sumar_minutos
from app.reglas.textos import normalizar_nombre


def controles_periodo(
    desde: date | None,
    hasta: date | None,
    hoy: date,
    cantidad_escrita: int | None = None,
    omitir_c9: bool = False,
) -> list[str]:
    """C2, C1, C9 y C10 sobre un período desde/hasta."""
    motivos: list[str] = []
    if desde and hasta:
        if hasta < desde:
            motivos.append(m.C2)
        else:
            dias = dias_inclusivos(desde, hasta)
            if cantidad_escrita is not None and cantidad_escrita != dias:
                motivos.append(m.c1(cantidad_escrita, dias))
            if not omitir_c9 and dias > DIAS_MAX_PERIODO:
                motivos.append(m.c9(dias))
    if desde and diferencia_dias(desde, hoy) > DIAS_MAX_ANTIGUEDAD:
        motivos.append(m.c10(DIAS_MAX_ANTIGUEDAD))
    return motivos


def control_tope_legal(
    tope: TopeLegal | None, tipo_legible: str | None, dias: int | None, cantidad_escrita: int | None
) -> list[str]:
    """C13: se compara el mayor entre los días del período y la cantidad escrita."""
    if tope is None:
        return []
    pedidos = max(dias or 0, cantidad_escrita or 0)
    return [m.c13(pedidos, tope.dias, tipo_legible or "", tope.norma)] if pedidos > tope.dias else []


def control_devolucion_anterior(fecha: date | None, fecha_devolucion: date | None) -> list[str]:
    """C5: devolución de horas anterior al retiro o ingreso."""
    if fecha and fecha_devolucion and fecha_devolucion < fecha:
        return [m.c5(formatear(fecha_devolucion), formatear(fecha))]
    return []


@dataclass
class ControlHoras:
    motivos_principal: list[str] = field(default_factory=list)
    motivos_devoluciones: list[str] = field(default_factory=list)
    adeudado: int | None = None
    devuelto: int | None = None


def control_horas_devolucion(
    codigo: int,
    hora: str | None,
    laboral_desde: str | None,
    laboral_hasta: str | None,
    devoluciones: list[tuple[str | None, str | None]],
) -> ControlHoras:
    """C12: lo adeudado por el retiro/ingreso tiene que coincidir con la suma de las devoluciones."""
    if not devoluciones:
        return ControlHoras()
    # El renglón sin alguna hora ya tiene su propio aviso; no se suma el de "no verificable".
    if any(desde is None or hasta is None for desde, hasta in devoluciones):
        return ControlHoras()
    if not hora or not laboral_desde or not laboral_hasta:
        return ControlHoras(motivos_devoluciones=[m.NO_SE_PUDO_VERIFICAR_HORAS])

    adeudado = (
        duracion_minutos(laboral_desde, hora) if codigo == 42 else duracion_minutos(hora, laboral_hasta)
    )
    if adeudado > duracion_minutos(laboral_desde, laboral_hasta):
        return ControlHoras(
            motivos_principal=[m.HORA_FUERA_DE_HORARIO], motivos_devoluciones=[m.NO_SE_PUDO_VERIFICAR_HORAS]
        )

    devuelto = sum(duracion_minutos(desde, hasta) for desde, hasta in devoluciones if desde and hasta)
    if adeudado == devuelto:
        return ControlHoras(adeudado=adeudado, devuelto=devuelto)
    return ControlHoras(
        motivos_devoluciones=[m.c12(formatear_duracion(adeudado), formatear_duracion(devuelto))],
        adeudado=adeudado,
        devuelto=devuelto,
    )


@dataclass(frozen=True)
class Tramo:
    indice: int
    fecha: date | None
    hora_desde: str | None
    hora_hasta: str | None
    a_favor: bool = False


def separar_excedente(renglones: list[Tramo], objetivo_min: int) -> tuple[list[Tramo], int] | None:
    """Parte los renglones en tramos que cubren exactamente el objetivo y tramos a favor.

    Se recorren en orden cronológico y el renglón donde se completa el objetivo se parte en dos.
    Devuelve None si falta alguna fecha u hora (no se puede ordenar ni cortar).
    """
    if any(not r.fecha or not r.hora_desde or not r.hora_hasta for r in renglones):
        return None
    ordenados = sorted(renglones, key=lambda r: (r.fecha, minutos(r.hora_desde or "")))
    tramos: list[Tramo] = []
    restante = objetivo_min
    total = 0
    for r in ordenados:
        duracion = duracion_minutos(r.hora_desde, r.hora_hasta)
        total += duracion
        if restante >= duracion:
            tramos.append(r)
            restante -= duracion
        elif restante > 0:
            corte, dias_extra = sumar_minutos(r.hora_desde, restante)
            tramos.append(replace(r, hora_hasta=corte))
            tramos.append(
                replace(r, fecha=r.fecha + timedelta(days=dias_extra), hora_desde=corte, a_favor=True)
            )
            restante = 0
        else:
            tramos.append(replace(r, a_favor=True))
    return tramos, total - objetivo_min


def control_mismo_dia_franco(fecha_trabajada: date | None, fecha_franco: date | None) -> list[str]:
    """C6. Un franco anterior al día trabajado está permitido."""
    if fecha_trabajada and fecha_franco and fecha_trabajada == fecha_franco:
        return [m.c6(formatear(fecha_franco))]
    return []


def control_misma_persona(solicitante: Persona | None, aceptante: Persona | None) -> list[str]:
    """C8: mismo legajo o mismo nombre normalizado."""
    if not solicitante or not aceptante:
        return []
    mismo_legajo = solicitante.legajo is not None and solicitante.legajo == aceptante.legajo
    nombre = normalizar_nombre(solicitante.nombre)
    mismo_nombre = nombre != "" and nombre == normalizar_nombre(aceptante.nombre)
    return [m.C8] if mismo_legajo or mismo_nombre else []
