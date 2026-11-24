"""Errores de la API con la forma {"codigo": "...", "mensaje": "..."} (y "errores" en validación)."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ErrorCampo:
    campo: str
    mensaje: str


class ErrorApi(Exception):
    def __init__(
        self, codigo: str, mensaje: str, status: int = 400, errores: list[ErrorCampo] | None = None
    ) -> None:
        super().__init__(mensaje)
        self.codigo = codigo
        self.mensaje = mensaje
        self.status = status
        self.errores = errores or []

    def como_json(self) -> dict[str, Any]:
        cuerpo: dict[str, Any] = {"codigo": self.codigo, "mensaje": self.mensaje}
        if self.errores:
            cuerpo["errores"] = [{"campo": e.campo, "mensaje": e.mensaje} for e in self.errores]
        return cuerpo


class ErrorValidacion(ErrorApi):
    def __init__(self, errores: list[ErrorCampo]) -> None:
        super().__init__("DATOS_INVALIDOS", "Revisá los datos marcados.", 422, errores)


def no_encontrada() -> ErrorApi:
    return ErrorApi("NO_ENCONTRADA", "La solicitud no existe o no tenés acceso.", 404)
