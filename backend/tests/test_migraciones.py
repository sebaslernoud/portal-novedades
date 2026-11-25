from alembic import command
from conftest import config_alembic
from sqlalchemy import inspect


def test_las_migraciones_bajan_y_suben(base_de_pruebas):
    config = config_alembic()
    command.downgrade(config, "base")
    assert set(inspect(base_de_pruebas).get_table_names()) == {"alembic_version"}
    command.upgrade(config, "head")
    tablas = set(inspect(base_de_pruebas).get_table_names())
    assert {"solicitudes", "auditoria", "lotes_exportacion", "novedades"} <= tablas
