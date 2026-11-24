from copy import deepcopy

import pytest

from app.cli import ejemplos
from app.reglas.fechas import hoy_negocio

EJEMPLOS = {cuerpo["tipo"]: (legajo, cuerpo) for legajo, cuerpo in ejemplos(hoy_negocio())}


def _crear(como, tipo: str, **cambios):
    legajo, cuerpo = deepcopy(EJEMPLOS[tipo])
    cuerpo.update(cambios)
    respuesta = como(legajo).post("/api/solicitudes", json=cuerpo)
    assert respuesta.status_code == 201, respuesta.get_json()
    return legajo, respuesta.get_json()


def test_sin_usuario_de_prueba_responde_401(como):
    for legajo in (None, 4242):
        respuesta = como(legajo).get("/api/solicitudes")
        assert respuesta.status_code == 401
        assert respuesta.get_json()["codigo"] == "SIN_USUARIO"


def test_usuarios(como, app):
    personas = como(None).get("/api/usuarios/prueba").get_json()
    assert len(personas) == 8 and {"legajo": 3001, "nombre": "SOFIA RAMIREZ"}.items() <= personas[-1].items()
    app.config["IDENTIDAD_DE_PRUEBA"] = False
    assert como(None).get("/api/usuarios/prueba").status_code == 401
    app.config["IDENTIDAD_DE_PRUEBA"] = True
    assert como(1001).get("/api/usuarios/actual").get_json()["roles"] == ["empleado"]
    jefes = como(2001).get("/api/usuarios/jefes").get_json()
    assert [j["legajo"] for j in jefes] == [2002]  # no se ofrece a sí mismo
    encontrados = como(1001).get("/api/usuarios?buscar=gom").get_json()
    assert encontrados == [{"legajo": 1002, "nombre": "ANA GOMEZ"}]


def test_crear_borrador_audita(como):
    legajo, solicitud = _crear(como, "franco_autorizado")
    assert solicitud["estado"] == "BORRADOR"
    assert solicitud["solicitante"] == {"legajo": legajo, "nombre": "LUCIA FERNANDEZ"}
    detalle = como(legajo).get(f"/api/solicitudes/{solicitud['id']}").get_json()
    assert [(a["accion"], a["estado_anterior"], a["estado_nuevo"]) for a in detalle["auditoria"]] == [
        ("crear", None, "BORRADOR")
    ]


def test_editar_borrador_solo_el_dueño(como):
    legajo, solicitud = _crear(como, "franco_autorizado")
    cuerpo = {"tipo": "franco_autorizado", "jefe_legajo": 2002, "datos": {"fecha_franco": "2026-12-10"}}
    assert como(1001).put(f"/api/solicitudes/{solicitud['id']}", json=cuerpo).status_code == 404
    editada = como(legajo).put(f"/api/solicitudes/{solicitud['id']}", json=cuerpo).get_json()
    assert editada["datos"] == {"fecha_franco": "2026-12-10"}


def test_enviar_incompleto_no_cambia_el_estado(como):
    legajo, solicitud = _crear(como, "retiro_ingreso", datos={"tipo_movimiento": "retiro"})
    respuesta = como(legajo).post(f"/api/solicitudes/{solicitud['id']}/enviar")
    assert respuesta.status_code == 422
    cuerpo = respuesta.get_json()
    assert cuerpo["codigo"] == "DATOS_INVALIDOS"
    assert {"campo": "datos.fecha", "mensaje": "Completá este campo."} in cuerpo["errores"]
    assert como(legajo).get(f"/api/solicitudes/{solicitud['id']}").get_json()["estado"] == "BORRADOR"


@pytest.mark.parametrize(
    ("tipo", "estado"),
    [
        ("retiro_ingreso", "PENDIENTE_JEFE"),
        ("licencia_especial", "PENDIENTE_JEFE"),
        ("franco_compensatorio", "PENDIENTE_JEFE"),
        ("franco_autorizado", "PENDIENTE_JEFE"),
        ("cambio_turno", "PENDIENTE_COMPANERO"),
    ],
)
def test_enviar_pasa_al_primer_paso_del_circuito(como, tipo, estado):
    legajo, solicitud = _crear(como, tipo)
    enviada = como(legajo).post(f"/api/solicitudes/{solicitud['id']}/enviar").get_json()
    assert enviada["estado"] == estado
    assert enviada["jefe"]["nombre"] and enviada["enviada_en"]
    assert enviada["advertencias"] == []
    detalle = como(legajo).get(f"/api/solicitudes/{solicitud['id']}").get_json()
    assert [a["accion"] for a in detalle["auditoria"]] == ["crear", "enviar"]
    # Una vez enviada no se puede editar ni volver a enviar.
    assert como(legajo).put(f"/api/solicitudes/{solicitud['id']}", json=EJEMPLOS[tipo][1]).status_code == 409
    assert como(legajo).post(f"/api/solicitudes/{solicitud['id']}/enviar").status_code == 409


def test_enviar_guarda_advertencias(como):
    datos = deepcopy(EJEMPLOS["retiro_ingreso"][1]["datos"])
    datos["devoluciones"] = []
    legajo, solicitud = _crear(como, "retiro_ingreso", datos=datos)
    enviada = como(legajo).post(f"/api/solicitudes/{solicitud['id']}/enviar").get_json()
    assert enviada["advertencias"] == ["No se cargó ninguna devolución de horas"]


def test_quien_puede_ver_el_detalle(como):
    legajo, solicitud = _crear(como, "cambio_turno")  # Juan, compañera Ana, jefa María
    url = f"/api/solicitudes/{solicitud['id']}"
    assert como(2001).get(url).status_code == 404  # borrador: solo el dueño
    como(legajo).post(f"{url}/enviar")
    for legajo_que_ve in (1001, 1002, 2001, 3001):
        assert como(legajo_que_ve).get(url).status_code == 200
    for legajo_que_no_ve in (1003, 2002):
        assert como(legajo_que_no_ve).get(url).status_code == 404


def test_listar_mias_y_donde_participo(como):
    legajo, solicitud = _crear(como, "cambio_turno")
    como(legajo).post(f"/api/solicitudes/{solicitud['id']}/enviar")
    assert [s["id"] for s in como(1001).get("/api/solicitudes").get_json()["mias"]] == [solicitud["id"]]
    de_ana = como(1002).get("/api/solicitudes").get_json()
    assert de_ana["mias"] == [] and [s["id"] for s in de_ana["donde_participo"]] == [solicitud["id"]]


def test_previsualizar_no_guarda_nada(como):
    legajo, cuerpo = EJEMPLOS["retiro_ingreso"]
    respuesta = como(legajo).post("/api/solicitudes/previsualizar", json=cuerpo)
    assert respuesta.status_code == 200
    resultado = respuesta.get_json()
    assert [n["concepto"] for n in resultado["novedades"]] == [26, 28]
    assert resultado["novedades"][0]["observaciones"].startswith("Retiro 16:00 hs. Devuelve el día")
    assert resultado["advertencias"] == []
    assert como(legajo).get("/api/solicitudes").get_json()["mias"] == []


def test_previsualizar_con_errores(como):
    respuesta = como(1001).post("/api/solicitudes/previsualizar", json={"tipo": "franco_autorizado"})
    assert respuesta.status_code == 422
    assert [e["campo"] for e in respuesta.get_json()["errores"]] == ["datos.fecha_franco", "jefe_legajo"]
