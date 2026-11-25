"""Exportación a GMS. Solo RR.HH."""

from io import BytesIO

from flask import jsonify, request, send_file

from app.api import api
from app.api.serializacion import lote_json, solicitud_json
from app.errores import ErrorApi
from app.exportacion import servicio
from app.identidad import Usuario, exigir_rol, usuario_actual

TIPO_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _rrhh() -> Usuario:
    usuario = usuario_actual()
    exigir_rol(usuario, "rrhh")
    return usuario


@api.get("/exportaciones/pendientes")
def listar_pendientes():
    usuario = _rrhh()
    return jsonify([solicitud_json(s, usuario) for s in servicio.listar_aprobadas()])


@api.get("/exportaciones")
def listar_exportaciones():
    _rrhh()
    return jsonify([lote_json(lote) for lote in servicio.listar_lotes()])


@api.post("/exportaciones")
def crear_exportacion():
    usuario = _rrhh()
    cuerpo = request.get_json(silent=True)
    ids = cuerpo.get("solicitudes") if isinstance(cuerpo, dict) else None
    if not isinstance(ids, list) or not all(isinstance(i, int) and not isinstance(i, bool) for i in ids):
        raise ErrorApi("CUERPO_INVALIDO", "Mandá la lista de solicitudes a exportar.", 400)
    return jsonify(lote_json(servicio.exportar(usuario, ids))), 201


@api.get("/exportaciones/<int:lote_id>/excel")
def descargar_excel(lote_id: int):
    _rrhh()
    lote = servicio.obtener_lote(lote_id)
    respuesta = send_file(
        BytesIO(servicio.excel_de_lote(lote)),
        mimetype=TIPO_XLSX,
        as_attachment=True,
        download_name=lote.nombre_archivo,
    )
    respuesta.headers["Cache-Control"] = "no-store"
    return respuesta
