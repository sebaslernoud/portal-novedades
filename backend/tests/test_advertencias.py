from datetime import date

from app.reglas.advertencias import calcular_advertencias
from app.reglas.entradas import (
    CambioTurno,
    FrancoAutorizado,
    FrancoCompensatorio,
    Persona,
    Renglon,
    RetiroIngreso,
)

HOY = date(2026, 11, 24)
JUAN = Persona(1001, "JUAN PEREZ")


def _retiro(devoluciones: list[Renglon]) -> RetiroIngreso:
    return RetiroIngreso(JUAN, "retiro", date(2026, 11, 25), "16:00", "09:00", "18:00", "Turno", devoluciones)


def test_sin_advertencias_si_todo_cierra():
    assert calcular_advertencias(_retiro([Renglon(date(2026, 11, 27), "18:00", "20:00")]), HOY) == []


def test_ri_4_retiro_sin_devoluciones():
    assert calcular_advertencias(_retiro([]), HOY) == ["No se cargó ninguna devolución de horas"]


def test_gen_1_fecha_a_mas_de_un_año():
    lejana = FrancoAutorizado(JUAN, date(2027, 12, 1))
    assert calcular_advertencias(lejana, HOY) == ["La fecha 01/12/2027 está a más de 1 año de hoy, confirmar"]
    assert calcular_advertencias(FrancoAutorizado(JUAN, date(2025, 11, 24)), HOY) == []


def test_motivos_del_motor_sin_repetir_entre_filas():
    franco = FrancoCompensatorio(
        JUAN,
        date(2026, 11, 30),
        "09:00",
        "13:00",
        dias_trabajados=[
            Renglon(date(2026, 11, 20), "18:00", "19:00"),
            Renglon(date(2026, 11, 21), "18:00", "19:00"),
        ],
    )
    # Las dos filas 28 traen el mismo aviso: se informa una vez.
    assert calcular_advertencias(franco, HOY) == [
        "Las horas no cierran: el franco es de 4 h y lo trabajado suma 2 h, confirmar"
    ]


def test_cambio_de_turno_devolucion_el_mismo_dia_no_advierte():
    mismo_dia = CambioTurno(JUAN, Persona(1002, "ANA GOMEZ"), date(2026, 12, 6), date(2026, 12, 6))
    assert calcular_advertencias(mismo_dia, HOY) == []
