"""Exportación de las solicitudes aprobadas al Excel de carga masiva de GMS.

Mientras no se defina la integración con GMS (especificación §7.1), RR.HH. baja el Excel y lo
importa a mano. Cada exportación es un lote: guarda la foto de las novedades para poder volver
a bajar exactamente el mismo archivo.
"""

from datetime import datetime

from sqlalchemy import select

from app.db import sesion
from app.errores import ErrorApi, ErrorCampo, ErrorValidacion
from app.excel import generar_excel, nombre_archivo, separar_validas
from app.identidad import Usuario
from app.modelos import EstadoSolicitud, LoteExportacion, Novedad, Solicitud
from app.reglas import FilaNovedad, generar_filas
from app.reglas.fechas import ahora_negocio
from app.solicitudes.servicio import auditar, validar_guardada

_CAMPOS_FILA = (
    "legajo",
    "concepto",
    "cantidad",
    "fecha_desde",
    "fecha_hasta",
    "observaciones",
    "anio_novedad",
    "mes_novedad",
    "fecha_validar_fichadas",
    "fecha_nov28",
    "hora_desde",
    "hora_hasta",
    "codigo_futuro",
)


def listar_aprobadas() -> list[Solicitud]:
    consulta = (
        select(Solicitud)
        .where(Solicitud.estado == EstadoSolicitud.APROBADA)
        .order_by(Solicitud.enviada_en, Solicitud.id)
    )
    return list(sesion.scalars(consulta))


def listar_lotes() -> list[LoteExportacion]:
    return list(sesion.scalars(select(LoteExportacion).order_by(LoteExportacion.id.desc())))


def exportar(usuario: Usuario, ids: list[int], ahora: datetime | None = None) -> LoteExportacion:
    """Todo o nada: si una sola fila no pasa la validación de GMS (§7.4), no se exporta ninguna."""
    if not ids:
        raise ErrorApi("SIN_SOLICITUDES", "Elegí al menos una solicitud para exportar.", 422)
    ahora = ahora or ahora_negocio()
    consulta = select(Solicitud).where(Solicitud.id.in_(set(ids))).order_by(Solicitud.id).with_for_update()
    solicitudes = list(sesion.scalars(consulta))
    if len(solicitudes) != len(set(ids)) or any(s.estado != EstadoSolicitud.APROBADA for s in solicitudes):
        sesion.rollback()
        raise ErrorApi(
            "NO_EXPORTABLE", "Alguna solicitud ya no está aprobada o no existe. Actualizá la lista.", 409
        )

    # AnioNovedad/mesNovedad salen de la fecha de exportación hasta que RR.HH. decida (§10.4).
    hoy = ahora.date()
    por_solicitud: list[tuple[Solicitud, list[FilaNovedad]]] = [
        (s, generar_filas(validar_guardada(s).entrada, hoy)) for s in solicitudes
    ]
    errores: list[ErrorCampo] = []
    for solicitud, filas in por_solicitud:
        _, errores_filas = separar_validas(filas)
        campo = f"solicitudes.{solicitud.id}"
        errores.extend(ErrorCampo(campo, f"{e.campo or 'fila'}: {e.mensaje}") for e in errores_filas)
    if errores:
        sesion.rollback()
        raise ErrorValidacion(errores)

    lote = LoteExportacion(
        creado_en=ahora,
        usuario_legajo=usuario.legajo,
        usuario_nombre=usuario.nombre,
        nombre_archivo=nombre_archivo("GMS", ahora),
        anio_novedad=hoy.year,
        mes_novedad=hoy.month,
        cantidad_filas=sum(len(filas) for _, filas in por_solicitud),
    )
    orden = 0
    for solicitud, filas in por_solicitud:
        for fila in filas:
            orden += 1
            valores = {campo: getattr(fila, campo) for campo in _CAMPOS_FILA}
            lote.novedades.append(
                Novedad(solicitud_id=solicitud.id, orden=orden, advertencias=list(fila.motivos), **valores)
            )
        lote.solicitudes.append(solicitud)
        auditar(solicitud, usuario, "rrhh", "exportar", EstadoSolicitud.EXPORTADA, ahora)
    sesion.add(lote)
    sesion.commit()
    return lote


def obtener_lote(lote_id: int) -> LoteExportacion:
    lote = sesion.get(LoteExportacion, lote_id)
    if lote is None:
        raise ErrorApi("NO_ENCONTRADO", "La exportación no existe.", 404)
    return lote


def excel_de_lote(lote: LoteExportacion) -> bytes:
    filas = [
        FilaNovedad(**{campo: getattr(n, campo) for campo in _CAMPOS_FILA}, motivos=list(n.advertencias))
        for n in lote.novedades
    ]
    return generar_excel(filas)
