"""Punto de entrada para gunicorn y `flask run`."""

from app import crear_app

app = crear_app()
