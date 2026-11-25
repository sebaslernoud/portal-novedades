"""Fixtures. Los tests con base usan `portal_novedades_test` (se crea sola) y no tocan la de desarrollo.

Cada test corre dentro de una transacción que se deshace al final, aunque el código haga commit.
"""

import os

from sqlalchemy.engine import make_url

_URL_DESARROLLO = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://portal:portal@localhost:5432/portal_novedades"
)
_url = make_url(_URL_DESARROLLO)
URL_PRUEBAS = _url.set(database=f"{_url.database}_test")
# Antes de importar la app: Config lee DATABASE_URL al importarse.
os.environ["DATABASE_URL"] = URL_PRUEBAS.render_as_string(hide_password=False)
os.environ["IDENTIDAD_DE_PRUEBA"] = "1"

from pathlib import Path  # noqa: E402

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config as ConfigAlembic  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402

from app import crear_app  # noqa: E402
from app.db import sesion  # noqa: E402
from app.identidad import HEADER_LEGAJO  # noqa: E402

RAIZ_BACKEND = Path(__file__).resolve().parents[1]


def _crear_base_si_falta() -> None:
    admin = create_engine(_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conexion:
        existe = conexion.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :nombre"), {"nombre": URL_PRUEBAS.database}
        ).scalar()
        if not existe:
            conexion.execute(text(f'CREATE DATABASE "{URL_PRUEBAS.database}"'))
    admin.dispose()


def config_alembic() -> ConfigAlembic:
    config = ConfigAlembic(str(RAIZ_BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(RAIZ_BACKEND / "migrations"))
    return config


@pytest.fixture(scope="session")
def base_de_pruebas():
    _crear_base_si_falta()
    command.upgrade(config_alembic(), "head")
    motor = create_engine(URL_PRUEBAS)
    yield motor
    motor.dispose()


@pytest.fixture
def app():
    return crear_app()


@pytest.fixture
def db(app, base_de_pruebas):
    """Sesión ligada a una transacción externa: los commit del código pasan a ser savepoints."""
    conexion = base_de_pruebas.connect()
    transaccion = conexion.begin()
    sesion.remove()
    sesion.configure(bind=conexion, join_transaction_mode="create_savepoint")
    with app.app_context():
        yield sesion
    sesion.remove()
    transaccion.rollback()
    conexion.close()
    sesion.configure(bind=app.extensions["motor_db"], join_transaction_mode="conservative_savepoint")


@pytest.fixture
def cliente(app):
    return app.test_client()


@pytest.fixture
def como(app, db):
    """Cliente que actúa como el legajo indicado: como(1001).get("/api/...")."""

    class _Cliente:
        def __init__(self, legajo: int | None) -> None:
            self._cliente = app.test_client()
            self._headers = {HEADER_LEGAJO: str(legajo)} if legajo else {}

        def __getattr__(self, metodo: str):
            funcion = getattr(self._cliente, metodo)
            return lambda *args, **kwargs: funcion(*args, headers=self._headers, **kwargs)

    return _Cliente
