"""Paridad con el motor de reglas de proyecto-auto-sc.

Cada caso de docs/casos-de-prueba-reglas.json trae la entrada (en el formato del motor original)
y las filas que tiene que producir el port a Python. Ver docs/REGLAS-DE-NEGOCIO.md, sección 13.
"""

import pytest
from casos_heredados import CASOS, HOY, a_solicitud, fila_como_en_el_caso

from app.reglas import generar_filas
from app.reglas.fechas import formatear


def test_hay_casos_de_prueba():
    assert len(CASOS) >= 25


def test_casos_generados_con_el_mismo_hoy():
    assert {c["hoy"] for c in CASOS} == {formatear(HOY)}


@pytest.mark.parametrize("caso", CASOS, ids=[c["nombre"] for c in CASOS])
def test_paridad_con_motor_original(caso):
    obtenidas = [fila_como_en_el_caso(f) for f in generar_filas(a_solicitud(caso), hoy=HOY)]
    esperadas = caso["filasEsperadas"]
    assert len(obtenidas) == len(esperadas)
    for i, (obtenida, esperada) in enumerate(zip(obtenidas, esperadas, strict=True)):
        assert list(obtenida) == list(esperada), f"fila {i}: campos distintos"
        assert obtenida == esperada, f"fila {i}"
