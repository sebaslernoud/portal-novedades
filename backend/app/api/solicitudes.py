"""Solicitudes: previsualizar, borradores, envío, consulta y circuito de aprobación."""

from flask import jsonify, request

from app.api import api
from app.api.serializacion import fila_json, solicitud_json
from app.identidad import usuario_actual
from app.solicitudes import servicio


@api.post("/solicitudes/previsualizar")
def previsualizar_solicitud():
    advertencias, filas = servicio.previsualizar(usuario_actual(), request.get_json(silent=True))
    return jsonify(advertencias=advertencias, novedades=[fila_json(f) for f in filas])


@api.post("/solicitudes")
def crear_solicitud():
    usuario = usuario_actual()
    solicitud = servicio.crear_borrador(usuario, request.get_json(silent=True))
    return jsonify(solicitud_json(solicitud, usuario)), 201


@api.put("/solicitudes/<int:solicitud_id>")
def editar_solicitud(solicitud_id: int):
    usuario = usuario_actual()
    solicitud = servicio.editar_borrador(usuario, solicitud_id, request.get_json(silent=True))
    return jsonify(solicitud_json(solicitud, usuario))


@api.post("/solicitudes/<int:solicitud_id>/enviar")
def enviar_solicitud(solicitud_id: int):
    usuario = usuario_actual()
    return jsonify(solicitud_json(servicio.enviar(usuario, solicitud_id), usuario))


@api.get("/solicitudes")
def listar_solicitudes():
    usuario = usuario_actual()
    return jsonify(
        mias=[solicitud_json(s, usuario) for s in servicio.listar_mias(usuario)],
        donde_participo=[solicitud_json(s, usuario) for s in servicio.listar_donde_participo(usuario)],
    )


@api.get("/solicitudes/<int:solicitud_id>")
def obtener_solicitud(solicitud_id: int):
    usuario = usuario_actual()
    return jsonify(solicitud_json(servicio.obtener_detalle(usuario, solicitud_id), usuario, detalle=True))


@api.get("/solicitudes/<int:solicitud_id>/novedades")
def obtener_novedades_previstas(solicitud_id: int):
    filas = servicio.novedades_previstas(usuario_actual(), solicitud_id)
    return jsonify([fila_json(f) for f in filas])


@api.post("/solicitudes/<int:solicitud_id>/aprobar")
def aprobar_solicitud(solicitud_id: int):
    usuario = usuario_actual()
    return jsonify(solicitud_json(servicio.aprobar(usuario, solicitud_id), usuario, detalle=True))


@api.post("/solicitudes/<int:solicitud_id>/rechazar")
def rechazar_solicitud(solicitud_id: int):
    usuario = usuario_actual()
    cuerpo = request.get_json(silent=True)
    motivo = cuerpo.get("motivo") if isinstance(cuerpo, dict) else None
    solicitud = servicio.rechazar(usuario, solicitud_id, motivo)
    return jsonify(solicitud_json(solicitud, usuario, detalle=True))


@api.get("/bandeja")
def obtener_bandeja():
    usuario = usuario_actual()
    grupos = servicio.bandeja(usuario)
    return jsonify({rol: [solicitud_json(s, usuario) for s in lista] for rol, lista in grupos.items()})
