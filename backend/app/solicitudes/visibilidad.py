"""Qué estado ve cada uno.

La exportación a GMS es un detalle interno de RR.HH.: el resto solo sabe si la novedad se cargó o
no. Se traduce en el backend para que el estado real ni siquiera viaje en la respuesta.
"""

from app.identidad import Usuario
from app.modelos import EstadoSolicitud

NO_CARGADA = "NO_CARGADA"
CARGADA = "CARGADA"

_PARA_EL_RESTO: dict[EstadoSolicitud, str] = {
    EstadoSolicitud.APROBADA: NO_CARGADA,
    EstadoSolicitud.ERROR_CARGA: NO_CARGADA,
    EstadoSolicitud.EXPORTADA: CARGADA,
    EstadoSolicitud.CARGADA_GMS: CARGADA,
}

# Acciones de la auditoría que el resto ve con otro nombre y sin la persona de RR.HH.
ACCION_EXPORTAR = "exportar"
ACCION_VISIBLE_EXPORTAR = "cargar"
NOMBRE_RRHH = "RR.HH."


def ve_todo(usuario: Usuario) -> bool:
    return usuario.tiene_rol("rrhh")


def estado_visible(estado: EstadoSolicitud, todo: bool) -> str:
    return estado.value if todo else _PARA_EL_RESTO.get(estado, estado.value)
