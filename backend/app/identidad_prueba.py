"""Directorio de personas FICTICIAS para desarrollo, mientras no exista el padrón.

Es la pieza que se reemplaza cuando se defina de dónde sale el padrón (GMS o carga manual).
"""

from app.identidad import Usuario

_EMPLEADO = frozenset({"empleado"})
_JEFE = frozenset({"empleado", "jefe"})
_RRHH = frozenset({"empleado", "rrhh"})

PERSONAS: tuple[Usuario, ...] = (
    Usuario(1001, "JUAN PEREZ", "4to piso", _EMPLEADO),
    Usuario(1002, "ANA GOMEZ", "4to piso", _EMPLEADO),
    Usuario(1003, "CARLOS DIAZ", "Planta baja", _EMPLEADO),
    Usuario(1004, "LUCIA FERNANDEZ", "Planta baja", _EMPLEADO),
    Usuario(1005, "PABLO SUAREZ", "Depósito", _EMPLEADO),
    Usuario(2001, "MARIA LOPEZ", "4to piso", _JEFE),
    Usuario(2002, "JORGE MARTINEZ", "Planta baja", _JEFE),
    Usuario(3001, "SOFIA RAMIREZ", "RR.HH.", _RRHH),
)
