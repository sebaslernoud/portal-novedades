"""Horas como texto "HH:MM" de 24 horas."""


def minutos(hora: str) -> int:
    hh, mm = hora.split(":")
    return int(hh) * 60 + int(mm)


def duracion_minutos(desde: str, hasta: str) -> int:
    """Minutos entre dos horas. Si el fin es menor que el inicio, cruza la medianoche (turno noche)."""
    inicio = minutos(desde)
    fin = minutos(hasta)
    if fin == inicio:
        return 0
    return fin - inicio if fin > inicio else fin + 1440 - inicio


def sumar_minutos(hora: str, cantidad: int) -> tuple[str, int]:
    """Devuelve la hora resultante y cuántas veces se pasó la medianoche."""
    total = minutos(hora) + cantidad
    en_el_dia = total % 1440
    return f"{en_el_dia // 60:02d}:{en_el_dia % 60:02d}", total // 1440


def formatear_duracion(cantidad: int) -> str:
    """Texto para las advertencias: 45 min, 3 h o 2 h 30 min."""
    horas, resto = divmod(cantidad, 60)
    if horas == 0:
        return f"{resto} min"
    if resto == 0:
        return f"{horas} h"
    return f"{horas} h {resto} min"


def hora_a_fraccion(hora: str) -> float:
    """Fracción de día, como Excel guarda las horas."""
    return minutos(hora) / 1440
