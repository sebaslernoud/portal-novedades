"""Textos de las advertencias. Centralizados porque agregar_motivos deduplica por texto idéntico."""

from datetime import date

FALTA_LEGAJO = "Falta el legajo"
COMPLETAR_HORA_HASTA = "Completar HORAHASTA a mano (depende del horario de la persona)"
FALTA_HORA_HASTA = "Falta HORAHASTA"
LICENCIA_NO_IDENTIFICADA = "Tipo de licencia especial no identificado, confirmar"
COMPLETAR_CODIGO_FUTURO = "Sin código futuro para este tipo de licencia; completar CODIGOFUTURO a mano"
C2 = "FechaHasta anterior a FechaDesde"
C8 = "Solicitante y aceptante tienen el mismo legajo o nombre"
NO_SE_PUDO_VERIFICAR_HORAS = (
    "No se pudo verificar que las horas de devolución cierren "
    "(falta el horario laboral o alguna hora), confirmar"
)
NO_SE_PUDO_VERIFICAR_HORAS_FRANCO = (
    "No se pudo verificar que las horas cierren "
    "(falta alguna hora del franco o de los días trabajados), confirmar"
)
HORA_FUERA_DE_HORARIO = "La hora del retiro/ingreso queda fuera del horario laboral declarado, confirmar"
GRUPO_CAMBIO_TURNO = "Otra fila del mismo cambio de turno requiere revisión; se revisan las 2 juntas"
COMPLETAR_FICHADA_FRANCO = (
    "El día trabajado es futuro; completar a mano una fecha ya trabajada para validar las fichadas"
)
FRANCO_SIN_FECHAS = "Formulario de franco sin fecha del franco ni día trabajado; completar a mano"
# Propias del portal (especificación §6), no existen en el motor heredado.
SIN_DEVOLUCIONES = "No se cargó ninguna devolución de horas"


def fecha_lejana(fecha: date) -> str:
    return f"La fecha {fecha.day:02d}/{fecha.month:02d}/{fecha.year} está a más de 1 año de hoy, confirmar"


def falta(campo: str) -> str:
    return f"Falta {campo}"


def falta_identificar(rol: str) -> str:
    return f"Falta identificar a {rol}"


def cambio_horario_fechas_distintas(cambio: str, devolucion: str) -> str:
    return (
        f"Cambio de horario con fecha de devolución ({devolucion}) distinta del día del cambio ({cambio}): "
        "confirmar si es un cambio de horario o un cambio de turno sin el compañero"
    )


def hasta_deducida_de_reintegro(reintegro: str) -> str:
    return f"FechaHasta deducida de la fecha de reintegro ({reintegro}), confirmar"


def cantidad_calculada(dias: int) -> str:
    return f"El formulario no indica la cantidad de días; se calcularon {dias} días corridos"


def c1(escrita: int, dias: int) -> str:
    return f"El formulario dice {escrita} días pero el período son {dias} días corridos"


def c5(fecha_devolucion: str, fecha: str) -> str:
    return f"La devolución ({fecha_devolucion}) es anterior al retiro/ingreso ({fecha}), confirmar"


def c6(fecha: str) -> str:
    return f"El franco y el día trabajado son el mismo día ({fecha}), confirmar"


def c9(dias: int) -> str:
    return f"Período de {dias} días, inusualmente largo, confirmar"


def c10(dias: int) -> str:
    return f"El período comenzó hace más de {dias} días, confirmar"


def c12(adeudado: str, devuelto: str) -> str:
    return f"Las horas no cierran: adeuda {adeudado} y devuelve {devuelto}, confirmar"


def c12_franco(franco: str, trabajado: str) -> str:
    return f"Las horas no cierran: el franco es de {franco} y lo trabajado suma {trabajado}, confirmar"


def c13(pedidos: int, tope: int, tipo: str, norma: str) -> str:
    return f"Se piden {pedidos} días de {tipo} y el máximo legal es {tope} ({norma}), confirmar"


def horas_a_favor(duracion: str) -> str:
    return f"Horas a favor: devuelve {duracion} más de lo que adeuda, confirmar si se registran"


def horas_a_favor_franco(duracion: str) -> str:
    return f"Horas a favor: trabajó {duracion} más de lo que dura el franco, confirmar si se registran"


def mas_renglones(cantidad: int, maximo: int) -> str:
    return f"El formulario tiene {cantidad} renglones de devolución y el máximo es {maximo}, confirmar"


def observaciones_largas(largo: int) -> str:
    return (
        f"Observaciones de {largo} caracteres: el máximo de GMS es 250, "
        "acortarlas a mano sin perder lo importante"
    )
