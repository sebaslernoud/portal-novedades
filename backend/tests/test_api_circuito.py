"""Circuito de aprobación y lo que ve cada uno. Personas del directorio de prueba:
Juan 1001 (solicitante), Ana 1002 (compañera), María 2001 (jefa), Sofía 3001 (RR.HH.)."""

import json
from copy import deepcopy

import pytest

from app.cli import ejemplos
from app.reglas.fechas import hoy_negocio

EJEMPLOS = {cuerpo["tipo"]: (legajo, cuerpo) for legajo, cuerpo in ejemplos(hoy_negocio())}
RRHH = 3001


def _enviada(como, tipo: str) -> int:
    legajo, cuerpo = deepcopy(EJEMPLOS[tipo])
    solicitud = como(legajo).post("/api/solicitudes", json=cuerpo).get_json()
    assert como(legajo).post(f"/api/solicitudes/{solicitud['id']}/enviar").status_code == 200
    return solicitud["id"]


def _aprobar(como, legajo: int, solicitud_id: int, status: int = 200) -> dict:
    respuesta = como(legajo).post(f"/api/solicitudes/{solicitud_id}/aprobar")
    assert respuesta.status_code == status, respuesta.get_json()
    return respuesta.get_json()


def test_recorrido_completo_del_cambio_de_turno(como):
    sid = _enviada(como, "cambio_turno")  # Juan, compañera Ana, jefa María
    assert como(1002).get(f"/api/solicitudes/{sid}").get_json()["acciones_disponibles"] == [
        "aprobar",
        "rechazar",
    ]
    assert como(2001).get(f"/api/solicitudes/{sid}").get_json()["acciones_disponibles"] == []

    assert _aprobar(como, 1002, sid)["estado"] == "PENDIENTE_JEFE"
    assert _aprobar(como, 2001, sid)["estado"] == "PENDIENTE_RRHH"
    assert _aprobar(como, RRHH, sid)["estado"] == "APROBADA"

    historial = como(RRHH).get(f"/api/solicitudes/{sid}").get_json()["auditoria"]
    assert [(a["accion"], a["rol"], a["estado_nuevo"]) for a in historial] == [
        ("crear", "solicitante", "BORRADOR"),
        ("enviar", "solicitante", "PENDIENTE_COMPANERO"),
        ("aceptar", "companero", "PENDIENTE_JEFE"),
        ("aprobar", "jefe", "PENDIENTE_RRHH"),
        ("aprobar", "rrhh", "APROBADA"),
    ]
    # Ya aprobada: llega a la exportación sin pasar por flask sembrar.
    assert [s["id"] for s in como(RRHH).get("/api/exportaciones/pendientes").get_json()] == [sid]


def test_sin_compañero_arranca_en_el_jefe(como):
    sid = _enviada(como, "franco_autorizado")  # Lucía, jefe Jorge
    _aprobar(como, 2001, sid, status=404)  # María no es la jefa asignada: ni la ve
    assert _aprobar(como, 2002, sid)["estado"] == "PENDIENTE_RRHH"


@pytest.mark.parametrize("paso", ["companero", "jefe", "rrhh"])
def test_rechazo_con_motivo_en_cada_paso(como, paso):
    sid = _enviada(como, "cambio_turno")
    actores = {"companero": 1002, "jefe": 2001, "rrhh": RRHH}
    for anterior in ["companero", "jefe", "rrhh"][: ["companero", "jefe", "rrhh"].index(paso)]:
        _aprobar(como, actores[anterior], sid)

    url = f"/api/solicitudes/{sid}/rechazar"
    sin_motivo = como(actores[paso]).post(url, json={"motivo": "no"})
    assert sin_motivo.status_code == 422
    assert sin_motivo.get_json()["errores"][0]["campo"] == "motivo"

    rechazada = como(actores[paso]).post(url, json={"motivo": "Ese día falta personal"}).get_json()
    assert rechazada["estado"] == "RECHAZADA"
    assert rechazada["auditoria"][-1]["motivo"] == "Ese día falta personal"
    assert rechazada["auditoria"][-1]["rol"] == paso
    # El rechazo es final.
    _aprobar(como, actores[paso], sid, status=409)


def test_permisos_y_estados(como):
    sid = _enviada(como, "cambio_turno")
    _aprobar(como, 1003, sid, status=404)  # no participa: ni siquiera la ve
    _aprobar(como, 1001, sid, status=403)  # el solicitante no se aprueba a sí mismo
    _aprobar(como, RRHH, sid, status=403)  # todavía no es su paso
    _aprobar(como, 1002, sid)
    _aprobar(como, 1002, sid, status=403)  # ya pasó al jefe


def test_rrhh_no_aprueba_lo_propio(como):
    legajo, cuerpo = deepcopy(EJEMPLOS["franco_autorizado"])
    sid = como(RRHH).post("/api/solicitudes", json=cuerpo).get_json()["id"]
    como(RRHH).post(f"/api/solicitudes/{sid}/enviar")
    _aprobar(como, 2002, sid)
    _aprobar(como, RRHH, sid, status=403)
    assert como(RRHH).get("/api/bandeja").get_json()["rrhh"] == []


def test_bandeja_de_cada_uno(como):
    cambio = _enviada(como, "cambio_turno")
    franco = _enviada(como, "franco_autorizado")

    def ids(legajo: int) -> dict[str, list[int]]:
        return {
            rol: [s["id"] for s in lista]
            for rol, lista in como(legajo).get("/api/bandeja").get_json().items()
        }

    assert ids(1002) == {"companero": [cambio], "jefe": [], "rrhh": []}
    assert ids(2002) == {"companero": [], "jefe": [franco], "rrhh": []}
    assert ids(1001) == {"companero": [], "jefe": [], "rrhh": []}
    _aprobar(como, 2002, franco)
    assert ids(RRHH) == {"companero": [], "jefe": [], "rrhh": [franco]}


def test_novedades_previstas_para_jefe_y_rrhh(como):
    sid = _enviada(como, "retiro_ingreso")  # Juan, jefa María
    filas = como(2001).get(f"/api/solicitudes/{sid}/novedades").get_json()
    assert [f["concepto"] for f in filas] == [26, 28]
    assert como(RRHH).get(f"/api/solicitudes/{sid}/novedades").status_code == 200
    assert como(1001).get(f"/api/solicitudes/{sid}/novedades").status_code == 403


def test_empleados_y_jefes_no_ven_la_exportacion(como):
    sid = _enviada(como, "cambio_turno")
    for legajo in (1002, 2001, RRHH):
        _aprobar(como, legajo, sid)

    def vista(legajo: int) -> dict:
        return como(legajo).get(f"/api/solicitudes/{sid}").get_json()

    for legajo in (1001, 1002, 2001):
        assert vista(legajo)["estado"] == "NO_CARGADA"
    assert vista(RRHH)["estado"] == "APROBADA"

    como(RRHH).post("/api/exportaciones", json={"solicitudes": [sid]})
    for legajo in (1001, 1002, 2001):
        cuerpo = vista(legajo)
        assert cuerpo["estado"] == "CARGADA"
        assert cuerpo["lote_exportacion_id"] is None
        assert cuerpo["auditoria"][-1] == {
            **cuerpo["auditoria"][-1],
            "accion": "cargar",
            "usuario": {"legajo": None, "nombre": "RR.HH."},
            "estado_nuevo": "CARGADA",
            "estado_anterior": "NO_CARGADA",
        }
        texto = json.dumps(cuerpo) + json.dumps(como(legajo).get("/api/solicitudes").get_json())
        assert (
            "EXPORTADA" not in texto and "exportar" not in texto and "SOFIA" not in texto.split("cargar")[-1]
        )
    rrhh = vista(RRHH)
    assert rrhh["estado"] == "EXPORTADA" and rrhh["lote_exportacion_id"] is not None
    assert rrhh["auditoria"][-1]["accion"] == "exportar"
