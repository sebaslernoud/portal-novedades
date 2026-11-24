from datetime import date

import pytest

from app.reglas.coherencia import Tramo, separar_excedente
from app.reglas.fila import FilaNovedad, agregar_motivos
from app.reglas.horas import duracion_minutos, formatear_duracion, sumar_minutos
from app.reglas.textos import lista_dias, normalizar_nombre, normalizar_observaciones, unir_partes


@pytest.mark.parametrize(
    ("desde", "hasta", "esperado"),
    [("09:00", "18:00", 540), ("22:00", "06:00", 480), ("10:00", "10:00", 0), ("23:30", "00:15", 45)],
)
def test_duracion_minutos_cruza_medianoche(desde, hasta, esperado):
    assert duracion_minutos(desde, hasta) == esperado


def test_sumar_minutos_cuenta_los_dias_extra():
    assert sumar_minutos("18:00", 120) == ("20:00", 0)
    assert sumar_minutos("23:00", 90) == ("00:30", 1)
    assert sumar_minutos("00:00", 1440 * 2 + 5) == ("00:05", 2)


@pytest.mark.parametrize(("minutos", "texto"), [(45, "45 min"), (180, "3 h"), (150, "2 h 30 min")])
def test_formatear_duracion(minutos, texto):
    assert formatear_duracion(minutos) == texto


def test_lista_dias_sin_repetir_y_ordenada():
    assert lista_dias([]) is None
    assert lista_dias([None]) is None
    assert lista_dias([date(2026, 11, 27)]) == "el día 27/11/2026"
    fechas = [date(2026, 11, 28), date(2026, 11, 26), date(2026, 11, 27), date(2026, 11, 26)]
    assert lista_dias(fechas) == "los días 26/11/2026, 27/11/2026 y 28/11/2026"


def test_unir_partes_y_normalizar_observaciones():
    assert unir_partes(["Retiro.", None, "  ", "Turno"]) == "Retiro. Turno"
    assert normalizar_observaciones("  a \n\t b  ") == "a b"
    assert normalizar_observaciones("   ") is None
    assert normalizar_observaciones("x" * 300) == "x" * 300


def test_normalizar_nombre_ignora_orden_acentos_y_mayusculas():
    assert normalizar_nombre("Pérez Juan") == normalizar_nombre("JUAN PEREZ") == "juan perez"
    assert normalizar_nombre(None) == ""


def test_agregar_motivos_no_repite():
    fila = FilaNovedad()
    agregar_motivos(fila, "a")
    agregar_motivos(fila, ["b", "a", "", "c"])
    assert fila.motivos == ["a", "b", "c"]


def test_separar_excedente_parte_el_renglon_y_pasa_la_medianoche():
    renglones = [
        Tramo(0, date(2026, 11, 27), "23:00", "02:00"),
        Tramo(1, date(2026, 11, 26), "18:00", "19:00"),
    ]
    resultado = separar_excedente(renglones, objetivo_min=150)
    assert resultado is not None
    tramos, a_favor = resultado
    assert a_favor == 90
    assert tramos == [
        Tramo(1, date(2026, 11, 26), "18:00", "19:00"),
        Tramo(0, date(2026, 11, 27), "23:00", "00:30"),
        Tramo(0, date(2026, 11, 28), "00:30", "02:00", a_favor=True),
    ]


def test_separar_excedente_sin_datos_completos():
    assert separar_excedente([Tramo(0, None, "18:00", "19:00")], 30) is None
