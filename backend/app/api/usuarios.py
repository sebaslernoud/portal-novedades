"""Usuario actual, jefes y buscador de compañeros."""

from flask import jsonify, request

from app.api import api
from app.api.serializacion import persona_json, usuario_json
from app.identidad import buscar_empleados, listar_jefes, personas_de_prueba, usuario_actual


@api.get("/usuarios/prueba")
def listar_usuarios_de_prueba():
    return jsonify([usuario_json(p) for p in personas_de_prueba()])


@api.get("/usuarios/actual")
def obtener_usuario_actual():
    return jsonify(usuario_json(usuario_actual()))


@api.get("/usuarios/jefes")
def obtener_jefes():
    usuario = usuario_actual()
    return jsonify([persona_json(j) for j in listar_jefes() if j.legajo != usuario.legajo])


@api.get("/usuarios")
def buscar_usuarios():
    usuario = usuario_actual()
    texto = request.args.get("buscar", "")
    return jsonify([persona_json(p) for p in buscar_empleados(texto) if p.legajo != usuario.legajo])
