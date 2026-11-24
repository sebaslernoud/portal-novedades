"""Tablas y umbrales heredados de proyecto-auto-sc (src/config.js y src/reglas/codigos.js)."""

from dataclasses import dataclass

# Única tabla válida de conceptos: lo que no esté acá no se exporta.
CODIGOS_NOVEDAD: dict[int, str] = {
    2: "Licencia por vacaciones",
    22: "Cambio de horario",
    26: "Retiro antes de hora autorizado",
    28: "Devolución de horas",
    37: "Cambio de turno",
    38: "Franco compensatorio",
    40: "Franco autorizado",
    41: "Ausencia con aviso",
    42: "Ingreso después de hora autorizado",
}

OBSERVACIONES_MAX_CARACTERES = 250
DIAS_MAX_PERIODO = 60
DIAS_MAX_ANTIGUEDAD = 120
MAX_RENGLONES_DEVOLUCION = 4


@dataclass(frozen=True)
class TopeLegal:
    dias: int
    norma: str


TIPOS_LICENCIA_LEGIBLES: dict[str, str] = {
    "matrimonio": "matrimonio",
    "pre_matrimoniales": "pre-matrimoniales",
    "nacimiento_adopcion": "nacimiento de hijos/adopción",
    "casamiento_hijos": "casamiento de hijos",
    "dador_sangre": "dador de sangre",
    "mudanza": "mudanza",
    "comparecencia_reparticiones_oficiales": "comparecencia ante reparticiones oficiales",
    "examen": "examen",
    "estudio": "estudio",
    "extraordinaria_sin_goce": "extraordinaria sin goce de haberes",
    "congreso": "congreso",
    "jornada_capacitacion": "jornada de capacitación",
    "festividad": "festividad",
    "maternidad": "maternidad",
    "estado_excedencia": "estado de excedencia",
}

# Código en que se transforma el 41 cuando el empleado entrega la documentación.
CODIGO_FUTURO_LICENCIA: dict[str, int] = {
    "matrimonio": 4,
    "pre_matrimoniales": 39,
    "nacimiento_adopcion": 8,
    "casamiento_hijos": 5,
    "dador_sangre": 1,
    "mudanza": 13,
    "comparecencia_reparticiones_oficiales": 12,
    "examen": 7,
    "estudio": 18,
    "extraordinaria_sin_goce": 16,
    "congreso": 30,
    "jornada_capacitacion": 43,
    "festividad": 53,
}

TOPES_LEGALES_LICENCIA: dict[str, TopeLegal] = {
    "matrimonio": TopeLegal(10, "LCT art. 158"),
    "nacimiento_adopcion": TopeLegal(3, "criterio de RR.HH."),
    "dador_sangre": TopeLegal(1, "Ley 22.990 art. 47"),
    "examen": TopeLegal(10, "LCT art. 158"),
    "maternidad": TopeLegal(90, "LCT art. 177"),
    "estado_excedencia": TopeLegal(184, "LCT art. 183"),
}

# En estas licencias el tope legal reemplaza al aviso de período largo (C9).
LICENCIAS_SIN_C9 = frozenset({"maternidad", "estado_excedencia"})
