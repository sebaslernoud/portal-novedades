"""Franco autorizado → una fila 40. Original: proyecto-auto-sc/src/reglas/francoAutorizado.js."""

from datetime import date

from app.reglas.comunes import asignar_persona, finalizar
from app.reglas.entradas import FrancoAutorizado
from app.reglas.fila import FilaNovedad, crear_fila
from app.reglas.textos import unir_partes


def regla_franco_autorizado(solicitud: FrancoAutorizado, hoy: date) -> list[FilaNovedad]:
    fila = crear_fila(hoy, concepto=40, cantidad=1)
    asignar_persona(fila, solicitud.persona)
    fila.fecha_desde = solicitud.fecha_franco
    fila.fecha_hasta = solicitud.fecha_franco
    fila.observaciones = unir_partes(["Franco autorizado.", solicitud.motivo])
    return finalizar([fila])
