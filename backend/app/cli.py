"""Comandos de desarrollo: `flask sembrar` crea solicitudes aprobadas FICTICIAS para probar la exportación.

Mientras no exista el circuito de aprobación, es la única forma de tener solicitudes en APROBADA.
"""

from datetime import date, timedelta
from typing import Any

import click
from flask import current_app
from flask.cli import with_appcontext

from app.db import sesion
from app.identidad import buscar_persona
from app.modelos import EstadoSolicitud
from app.reglas.fechas import ahora_negocio
from app.solicitudes.servicio import auditar, crear_borrador, enviar

LEGAJO_RRHH_PRUEBA = 3001


def ejemplos(hoy: date) -> list[tuple[int, dict[str, Any]]]:
    """(legajo del solicitante, cuerpo del formulario). Fechas relativas a hoy para no disparar GEN-1."""

    def dia(n: int) -> str:
        return (hoy + timedelta(days=n)).isoformat()

    return [
        (1001, {"tipo": "retiro_ingreso", "jefe_legajo": 2001, "datos": {
            "tipo_movimiento": "retiro", "fecha": dia(1), "hora": "16:00",
            "horario_laboral_desde": "09:00", "horario_laboral_hasta": "18:00", "motivo": "Turno médico",
            "devoluciones": [{"fecha": dia(3), "hora_desde": "18:00", "hora_hasta": "20:00"}],
        }}),
        (1002, {"tipo": "licencia_especial", "jefe_legajo": 2001, "datos": {
            "tipo_licencia": "matrimonio", "fecha_desde": dia(7), "fecha_hasta": dia(16),
        }}),
        (1003, {"tipo": "franco_compensatorio", "jefe_legajo": 2002, "datos": {
            "fecha_franco": dia(6), "hora_desde_franco": "09:00", "hora_hasta_franco": "13:00",
            "dias_trabajados": [
                {"fecha": dia(-4), "hora_desde": "18:00", "hora_hasta": "20:00"},
                {"fecha": dia(-3), "hora_desde": "18:00", "hora_hasta": "20:00"},
            ],
            "motivo": "Cierre de mes",
        }}),
        (1004, {"tipo": "franco_autorizado", "jefe_legajo": 2002, "datos": {
            "fecha_franco": dia(8), "motivo": "Cumpleaños",
        }}),
        (1001, {"tipo": "cambio_turno", "jefe_legajo": 2001, "datos": {
            "companero_legajo": 1002, "fecha_cambio": dia(12), "fecha_devolucion": dia(15),
        }}),
    ]  # fmt: skip


@click.command("sembrar")
@with_appcontext
def sembrar() -> None:
    """Crea una solicitud aprobada de cada formulario, con datos ficticios."""
    if not current_app.config.get("IDENTIDAD_DE_PRUEBA"):
        raise click.ClickException("Solo disponible con IDENTIDAD_DE_PRUEBA activa (desarrollo).")
    rrhh = buscar_persona(LEGAJO_RRHH_PRUEBA)
    ahora = ahora_negocio()
    creadas = 0
    for legajo, cuerpo in ejemplos(ahora.date()):
        usuario = buscar_persona(legajo)
        if usuario is None or rrhh is None:
            raise click.ClickException("Falta una persona en el directorio de prueba.")
        solicitud = enviar(usuario, crear_borrador(usuario, cuerpo, ahora).id, ahora)
        auditar(
            solicitud, rrhh, "sistema", "sembrar", EstadoSolicitud.APROBADA, ahora,
            motivo="Aprobada sin circuito: sembrada para desarrollo",
        )  # fmt: skip
        sesion.commit()
        creadas += 1
    click.echo(f"Se crearon {creadas} solicitudes aprobadas de prueba.")
