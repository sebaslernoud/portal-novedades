"""Borradores, envío y consulta de solicitudes. Cada cambio de estado queda auditado."""

from datetime import date, datetime
from typing import Any

from sqlalchemy import or_, select

from app.db import sesion
from app.errores import ErrorApi, no_encontrada
from app.identidad import Usuario, buscar_persona
from app.modelos import EstadoSolicitud, RegistroAuditoria, Solicitud, TipoSolicitud
from app.reglas import FilaNovedad, generar_filas
from app.reglas.advertencias import calcular_advertencias
from app.reglas.fechas import ahora_negocio
from app.solicitudes.validacion import Borrador, SolicitudValidada, validar_borrador, validar_envio

# Estados en los que la solicitud ya no es un borrador privado del solicitante.
_VISIBLES_PARA_OTROS = frozenset(EstadoSolicitud) - {EstadoSolicitud.BORRADOR}


def auditar(
    solicitud: Solicitud,
    usuario: Usuario,
    rol: str,
    accion: str,
    estado_nuevo: EstadoSolicitud,
    ahora: datetime,
    motivo: str | None = None,
    detalle: dict[str, Any] | None = None,
) -> None:
    estado_anterior = solicitud.estado  # None si la solicitud es nueva
    solicitud.estado = estado_nuevo
    solicitud.auditoria.append(
        RegistroAuditoria(
            usuario_legajo=usuario.legajo,
            usuario_nombre=usuario.nombre,
            rol=rol,
            accion=accion,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            motivo=motivo,
            detalle=detalle,
            creado_en=ahora,
        )
    )


def _borrador_de(solicitud: Solicitud) -> Borrador:
    return Borrador(solicitud.tipo, solicitud.jefe_legajo, solicitud.comentario, solicitud.datos)


def validar_guardada(solicitud: Solicitud) -> SolicitudValidada:
    """Vuelve a armar la entrada del motor a partir de lo guardado (se usa al exportar)."""
    solicitante = buscar_persona(solicitud.solicitante_legajo) or Usuario(
        solicitud.solicitante_legajo, solicitud.solicitante_nombre, None, frozenset()
    )
    return validar_envio(solicitante, _borrador_de(solicitud))


def crear_borrador(usuario: Usuario, cuerpo: Any, ahora: datetime | None = None) -> Solicitud:
    borrador = validar_borrador(cuerpo)
    ahora = ahora or ahora_negocio()
    solicitud = Solicitud(
        tipo=borrador.tipo,
        solicitante_legajo=usuario.legajo,
        solicitante_nombre=usuario.nombre,
        jefe_legajo=borrador.jefe_legajo,
        comentario=borrador.comentario,
        datos=borrador.datos,
        advertencias=[],
        creada_en=ahora,
    )
    auditar(solicitud, usuario, "solicitante", "crear", EstadoSolicitud.BORRADOR, ahora)
    sesion.add(solicitud)
    sesion.commit()
    return solicitud


def _borrador_propio(usuario: Usuario, solicitud_id: int) -> Solicitud:
    solicitud = sesion.get(Solicitud, solicitud_id, with_for_update=True)
    if solicitud is None or solicitud.solicitante_legajo != usuario.legajo:
        raise no_encontrada()
    if solicitud.estado != EstadoSolicitud.BORRADOR:
        # Inmutabilidad (§3.3): una vez enviada, el solicitante no puede editar los datos.
        raise ErrorApi("YA_ENVIADA", "La solicitud ya fue enviada y no se puede modificar.", 409)
    return solicitud


def editar_borrador(usuario: Usuario, solicitud_id: int, cuerpo: Any) -> Solicitud:
    solicitud = _borrador_propio(usuario, solicitud_id)
    borrador = validar_borrador(cuerpo)
    solicitud.tipo = borrador.tipo
    solicitud.jefe_legajo = borrador.jefe_legajo
    solicitud.comentario = borrador.comentario
    solicitud.datos = borrador.datos
    sesion.commit()
    return solicitud


def aplicar_envio(
    solicitud: Solicitud, usuario: Usuario, validada: SolicitudValidada, ahora: datetime
) -> None:
    """Pasa un borrador validado al primer paso del circuito."""
    solicitud.datos = validada.datos
    solicitud.jefe_legajo = validada.jefe.legajo
    solicitud.jefe_nombre = validada.jefe.nombre
    solicitud.companero_legajo = validada.companero.legajo if validada.companero else None
    solicitud.companero_nombre = validada.companero.nombre if validada.companero else None
    solicitud.advertencias = calcular_advertencias(validada.entrada, ahora.date())
    solicitud.enviada_en = ahora
    siguiente = (
        EstadoSolicitud.PENDIENTE_COMPANERO
        if validada.tipo == TipoSolicitud.CAMBIO_TURNO
        else EstadoSolicitud.PENDIENTE_JEFE
    )
    auditar(solicitud, usuario, "solicitante", "enviar", siguiente, ahora)


def enviar(usuario: Usuario, solicitud_id: int, ahora: datetime | None = None) -> Solicitud:
    solicitud = _borrador_propio(usuario, solicitud_id)
    validada = validar_envio(usuario, _borrador_de(solicitud))
    aplicar_envio(solicitud, usuario, validada, ahora or ahora_negocio())
    sesion.commit()
    return solicitud


def previsualizar(
    usuario: Usuario, cuerpo: Any, hoy: date | None = None
) -> tuple[list[str], list[FilaNovedad]]:
    """Advertencias y novedades que generaría la solicitud, sin guardar nada."""
    hoy = hoy or ahora_negocio().date()
    validada = validar_envio(usuario, validar_borrador(cuerpo))
    return calcular_advertencias(validada.entrada, hoy), generar_filas(validada.entrada, hoy)


def listar_mias(usuario: Usuario) -> list[Solicitud]:
    consulta = (
        select(Solicitud)
        .where(Solicitud.solicitante_legajo == usuario.legajo)
        .order_by(Solicitud.creada_en.desc(), Solicitud.id.desc())
    )
    return list(sesion.scalars(consulta))


def listar_donde_participo(usuario: Usuario) -> list[Solicitud]:
    """Solicitudes de otros donde el usuario es compañero o jefe asignado."""
    consulta = (
        select(Solicitud)
        .where(
            Solicitud.estado.in_(_VISIBLES_PARA_OTROS),
            Solicitud.solicitante_legajo != usuario.legajo,
            or_(Solicitud.companero_legajo == usuario.legajo, Solicitud.jefe_legajo == usuario.legajo),
        )
        .order_by(Solicitud.enviada_en.desc(), Solicitud.id.desc())
    )
    return list(sesion.scalars(consulta))


def obtener_detalle(usuario: Usuario, solicitud_id: int) -> Solicitud:
    solicitud = sesion.get(Solicitud, solicitud_id)
    if solicitud is None or not puede_ver(usuario, solicitud):
        raise no_encontrada()
    return solicitud


def puede_ver(usuario: Usuario, solicitud: Solicitud) -> bool:
    """Matriz de permisos (§2.1): propias, donde participa, asignadas o, para RR.HH., todas."""
    if solicitud.solicitante_legajo == usuario.legajo:
        return True
    if solicitud.estado == EstadoSolicitud.BORRADOR:
        return False
    return (
        usuario.tiene_rol("rrhh")
        or solicitud.companero_legajo == usuario.legajo
        or solicitud.jefe_legajo == usuario.legajo
    )
