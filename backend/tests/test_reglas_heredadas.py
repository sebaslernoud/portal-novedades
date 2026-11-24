"""Paridad con el motor de reglas de proyecto-auto-sc.

Cada caso de docs/casos-de-prueba-reglas.json trae la entrada (en el formato del motor original)
y las filas que tiene que producir el port a Python. Ver docs/REGLAS-DE-NEGOCIO.md, sección 13.
Mientras las reglas no estén portadas, los casos se marcan como pendientes (skip).
"""

import json
import os
from pathlib import Path

import pytest


def _ruta_casos() -> Path:
    if os.environ.get("CASOS_REGLAS"):
        return Path(os.environ["CASOS_REGLAS"])
    # Local: backend/tests → raíz del repo. En Docker, docs/ se monta en /docs.
    return Path(__file__).resolve().parents[2] / "docs" / "casos-de-prueba-reglas.json"


CASOS = json.loads(_ruta_casos().read_text(encoding="utf-8"))["casos"]


def test_hay_casos_de_prueba():
    assert len(CASOS) >= 25


@pytest.mark.parametrize("caso", CASOS, ids=[c["nombre"] for c in CASOS])
def test_paridad_con_motor_original(caso):
    pytest.skip("Reglas todavía no portadas (app/reglas)")
