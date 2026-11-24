"""Quién es el usuario y quiénes son los demás empleados.

Hoy el usuario sale del header X-Legajo-Prueba y las personas, de un directorio ficticio
(app/identidad_prueba.py). Cuando se definan el login y el padrón (Fase 0 del CLAUDE.md), se
reemplaza la implementación de estas funciones y el resto del código no cambia.
"""

from dataclasses import dataclass
from typing import Literal

from flask import current_app, request

from app.errores import ErrorApi

Rol = Literal["empleado", "jefe", "rrhh"]
HEADER_LEGAJO = "X-Legajo-Prueba"


@dataclass(frozen=True)
class Usuario:
    legajo: int
    nombre: str
    sector: str | None
    roles: frozenset[str]

    def tiene_rol(self, rol: Rol) -> bool:
        return rol in self.roles


def _personas() -> tuple[Usuario, ...]:
    from app.identidad_prueba import PERSONAS

    return PERSONAS


def buscar_persona(legajo: int) -> Usuario | None:
    return next((p for p in _personas() if p.legajo == legajo), None)


def listar_jefes() -> list[Usuario]:
    return [p for p in _personas() if p.tiene_rol("jefe")]


def buscar_empleados(texto: str) -> list[Usuario]:
    """Por legajo o por parte del nombre, sin distinguir mayúsculas."""
    texto = texto.strip().lower()
    if not texto:
        return []
    return [p for p in _personas() if texto in str(p.legajo) or texto in p.nombre.lower()]


def personas_de_prueba() -> tuple[Usuario, ...]:
    """Para el selector de usuario de la pantalla. Solo existe mientras no haya login."""
    if not current_app.config.get("IDENTIDAD_DE_PRUEBA"):
        raise ErrorApi("SIN_LOGIN", "El ingreso de usuarios todavía no está disponible.", 401)
    return _personas()


def usuario_actual() -> Usuario:
    if not current_app.config.get("IDENTIDAD_DE_PRUEBA"):
        raise ErrorApi("SIN_LOGIN", "El ingreso de usuarios todavía no está disponible.", 401)
    valor = request.headers.get(HEADER_LEGAJO, "").strip()
    usuario = buscar_persona(int(valor)) if valor.isdigit() else None
    if usuario is None:
        raise ErrorApi("SIN_USUARIO", "Elegí un usuario de prueba para continuar.", 401)
    return usuario


def exigir_rol(usuario: Usuario, rol: Rol) -> None:
    if not usuario.tiene_rol(rol):
        raise ErrorApi("SIN_PERMISO", "No tenés permiso para hacer esto.", 403)
