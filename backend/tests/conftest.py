import pytest

from app import crear_app


@pytest.fixture
def app():
    return crear_app()


@pytest.fixture
def cliente(app):
    return app.test_client()
