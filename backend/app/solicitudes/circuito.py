"""Circuito de aprobación (especificación §3): compañero (solo cambio de turno) → jefe → RR.HH.

Funciones puras: quién tiene el paso en cada estado y adónde va la solicitud. Supuestos vigentes
hasta que RR.HH. decida: aprueba un solo jefe (el que eligió el solicitante), el rechazo es final
y las solicitudes no vencen.
"""

from dataclasses import dataclass
from typing import Literal

from app.errores import ErrorCampo, ErrorValidacion
from app.identidad import Usuario
from app.modelos import EstadoSolicitud, Solicitud

Accion = Literal["aprobar", "rechazar"]
RolPaso = Literal["companero", "jefe", "rrhh"]

MOTIVO_MINIMO = 5
MOTIVO_MAXIMO = 500


@dataclass(frozen=True)
class Paso:
    rol: RolPaso
    al_aprobar: EstadoSolicitud
    # Nombre de la acción en la auditoría: el compañero "acepta", el resto "aprueba".
    accion_aprobar: str


PASOS: dict[EstadoSolicitud, Paso] = {
    EstadoSolicitud.PENDIENTE_COMPANERO: Paso("companero", EstadoSolicitud.PENDIENTE_JEFE, "aceptar"),
    EstadoSolicitud.PENDIENTE_JEFE: Paso("jefe", EstadoSolicitud.PENDIENTE_RRHH, "aprobar"),
    EstadoSolicitud.PENDIENTE_RRHH: Paso("rrhh", EstadoSolicitud.APROBADA, "aprobar"),
}


def paso_actual(solicitud: Solicitud) -> Paso | None:
    return PASOS.get(solicitud.estado)


def tiene_el_paso(usuario: Usuario, solicitud: Solicitud) -> bool:
    paso = paso_actual(solicitud)
    if paso is None:
        return False
    match paso.rol:
        case "companero":
            return solicitud.companero_legajo == usuario.legajo
        case "jefe":
            return solicitud.jefe_legajo == usuario.legajo
        case "rrhh":
            # Nadie aprueba su propia solicitud, aunque sea de RR.HH.
            return usuario.tiene_rol("rrhh") and solicitud.solicitante_legajo != usuario.legajo
    return False


def acciones_disponibles(usuario: Usuario, solicitud: Solicitud) -> list[Accion]:
    return ["aprobar", "rechazar"] if tiene_el_paso(usuario, solicitud) else []


def validar_motivo(motivo: object) -> str:
    texto = motivo.strip() if isinstance(motivo, str) else ""
    if len(texto) < MOTIVO_MINIMO:
        mensaje = f"Escribí el motivo del rechazo (mínimo {MOTIVO_MINIMO} caracteres)."
    elif len(texto) > MOTIVO_MAXIMO:
        mensaje = f"Máximo {MOTIVO_MAXIMO} caracteres."
    else:
        return texto
    raise ErrorValidacion([ErrorCampo("motivo", mensaje)])
