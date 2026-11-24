"""Solicitudes: previsualizar, borradores, envío y consulta."""

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
    solicitud = servicio.crear_borrador(usuario_actual(), request.get_json(silent=True))
    return jsonify(solicitud_json(solicitud)), 201


@api.put("/solicitudes/<int:solicitud_id>")
def editar_solicitud(solicitud_id: int):
    solicitud = servicio.editar_borrador(usuario_actual(), solicitud_id, request.get_json(silent=True))
    return jsonify(solicitud_json(solicitud))


@api.post("/solicitudes/<int:solicitud_id>/enviar")
def enviar_solicitud(solicitud_id: int):
    return jsonify(solicitud_json(servicio.enviar(usuario_actual(), solicitud_id)))


@api.get("/solicitudes")
def listar_solicitudes():
    usuario = usuario_actual()
    return jsonify(
        mias=[solicitud_json(s) for s in servicio.listar_mias(usuario)],
        donde_participo=[solicitud_json(s) for s in servicio.listar_donde_participo(usuario)],
    )


@api.get("/solicitudes/<int:solicitud_id>")
def obtener_solicitud(solicitud_id: int):
    solicitud = servicio.obtener_detalle(usuario_actual(), solicitud_id)
    return jsonify(solicitud_json(solicitud, con_auditoria=True))
