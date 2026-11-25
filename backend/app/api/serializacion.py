"""Conversión de modelos a JSON. Fechas en ISO (AAAA-MM-DD), horas "HH:MM"."""

from dataclasses import asdict
from datetime import date, datetime
from typing import Any

from app.identidad import Usuario
from app.modelos import LoteExportacion, RegistroAuditoria, Solicitud
from app.reglas import FilaNovedad


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


def solicitud_json(solicitud: Solicitud, con_auditoria: bool = False) -> dict[str, Any]:
    cuerpo: dict[str, Any] = {
        "id": solicitud.id,
        "tipo": solicitud.tipo.value,
        "estado": solicitud.estado.value,
        "solicitante": _persona(solicitud.solicitante_legajo, solicitud.solicitante_nombre),
        "jefe": _persona(solicitud.jefe_legajo, solicitud.jefe_nombre),
        "jefe_legajo": solicitud.jefe_legajo,
        "companero": _persona(solicitud.companero_legajo, solicitud.companero_nombre),
        "datos": solicitud.datos,
        "comentario": solicitud.comentario,
        "advertencias": solicitud.advertencias,
        "creada_en": _iso(solicitud.creada_en),
        "enviada_en": _iso(solicitud.enviada_en),
        "lote_exportacion_id": solicitud.lote_exportacion_id,
    }
    if con_auditoria:
        cuerpo["auditoria"] = [auditoria_json(r) for r in solicitud.auditoria]
    return cuerpo


def auditoria_json(registro: RegistroAuditoria) -> dict[str, Any]:
    return {
        "usuario": _persona(registro.usuario_legajo, registro.usuario_nombre),
        "rol": registro.rol,
        "accion": registro.accion,
        "estado_anterior": registro.estado_anterior.value if registro.estado_anterior else None,
        "estado_nuevo": registro.estado_nuevo.value,
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
