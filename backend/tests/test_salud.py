"""GET /api/salud contra la base de pruebas, ya migrada a la última revisión."""

from alembic.script import ScriptDirectory
from conftest import config_alembic


def test_salud_informa_base_y_migracion(cliente, db):
    respuesta = cliente.get("/api/salud")

    ultima = ScriptDirectory.from_config(config_alembic()).get_current_head()
    assert respuesta.status_code == 200
    assert respuesta.get_json() == {"estado": "ok", "base_de_datos": "ok", "migracion": ultima}
