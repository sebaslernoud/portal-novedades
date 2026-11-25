"""Conversión de modelos a JSON. Fechas en ISO (AAAA-MM-DD), horas "HH:MM"."""

from dataclasses import asdict
from datetime import date, datetime
from typing import Any

from app.identidad import Usuario
from app.modelos import LoteExportacion, RegistroAuditoria, Solicitud
from app.reglas import FilaNovedad
from app.solicitudes.circuito import acciones_disponibles
from app.solicitudes.visibilidad import (
    ACCION_EXPORTAR,
    ACCION_VISIBLE_EXPORTAR,
    NOMBRE_RRHH,
    estado_visible,
    ve_todo,
)


def _iso(valor: date | datetime | None) -> str | None:
    return valor.isoformat() if valor else None


def usuario_json(usuario: Usuario) -> dict[str, Any]:
    return {
        "legajo": usuario.legajo,
        "nombre": usuario.nombre,
        "sector": usuario.sector,
        "roles": sorted(usuario.roles),
    }


def persona_json(usuario: Usuario) -> dict[str, Any]:
    return {"legajo": usuario.legajo, "nombre": usuario.nombre}


def _persona(legajo: int | None, nombre: str | None) -> dict[str, Any] | None:
    return {"legajo": legajo, "nombre": nombre} if legajo is not None else None


def solicitud_json(solicitud: Solicitud, usuario: Usuario, detalle: bool = False) -> dict[str, Any]:
    """Lo que ve `usuario`: quien no es RR.HH. no ve la exportación a GMS (ver visibilidad.py)."""
    todo = ve_todo(usuario)
    cuerpo: dict[str, Any] = {
        "id": solicitud.id,
        "tipo": solicitud.tipo.value,
        "estado": estado_visible(solicitud.estado, todo),
        "solicitante": _persona(solicitud.solicitante_legajo, solicitud.solicitante_nombre),
        "jefe": _persona(solicitud.jefe_legajo, solicitud.jefe_nombre),
        "jefe_legajo": solicitud.jefe_legajo,
        "companero": _persona(solicitud.companero_legajo, solicitud.companero_nombre),
        "datos": solicitud.datos,
        "comentario": solicitud.comentario,
        "advertencias": solicitud.advertencias,
        "creada_en": _iso(solicitud.creada_en),
        "enviada_en": _iso(solicitud.enviada_en),
        "lote_exportacion_id": solicitud.lote_exportacion_id if todo else None,
    }
    if detalle:
        cuerpo["auditoria"] = [auditoria_json(r, todo) for r in solicitud.auditoria]
        cuerpo["acciones_disponibles"] = acciones_disponibles(usuario, solicitud)
    return cuerpo


def auditoria_json(registro: RegistroAuditoria, todo: bool) -> dict[str, Any]:
    usuario = _persona(registro.usuario_legajo, registro.usuario_nombre)
    accion = registro.accion
    if not todo and accion == ACCION_EXPORTAR:
        usuario = {"legajo": None, "nombre": NOMBRE_RRHH}
        accion = ACCION_VISIBLE_EXPORTAR
    return {
        "usuario": usuario,
        "rol": registro.rol,
        "accion": accion,
        "estado_anterior": estado_visible(registro.estado_anterior, todo)
        if registro.estado_anterior
        else None,
        "estado_nuevo": estado_visible(registro.estado_nuevo, todo),
        "motivo": registro.motivo,
        "creado_en": _iso(registro.creado_en),
    }


def fila_json(fila: FilaNovedad) -> dict[str, Any]:
    datos = asdict(fila)
    datos.pop("a_favor")
    return {k: _iso(v) if isinstance(v, date) else v for k, v in datos.items()}


def lote_json(lote: LoteExportacion) -> dict[str, Any]:
    return {
        "id": lote.id,
        "creado_en": _iso(lote.creado_en),
        "usuario": _persona(lote.usuario_legajo, lote.usuario_nombre),
        "nombre_archivo": lote.nombre_archivo,
        "anio_novedad": lote.anio_novedad,
        "mes_novedad": lote.mes_novedad,
        "cantidad_filas": lote.cantidad_filas,
        "cantidad_solicitudes": len(lote.solicitudes),
    }
