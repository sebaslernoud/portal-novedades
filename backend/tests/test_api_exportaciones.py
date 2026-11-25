from copy import deepcopy
from datetime import datetime
from io import BytesIO

import pytest
from openpyxl import load_workbook

from app.cli import ejemplos, sembrar
from app.db import sesion
from app.exportacion import servicio
from app.identidad import buscar_persona
from app.modelos import EstadoSolicitud, Solicitud
from app.reglas.fechas import ZONA_NEGOCIO, hoy_negocio
from app.solicitudes.servicio import auditar, crear_borrador, enviar

RRHH = 3001


@pytest.fixture
def aprobadas(app, db) -> list[int]:
    resultado = app.test_cli_runner().invoke(sembrar)
    assert resultado.exit_code == 0, resultado.output
    return [s.id for s in servicio.listar_aprobadas()]


def _aprobar_retiro_con_motivo(motivo: str) -> int:
    legajo, cuerpo = deepcopy(next(e for e in ejemplos(hoy_negocio()) if e[1]["tipo"] == "retiro_ingreso"))
    cuerpo["datos"]["motivo"] = motivo
    usuario, rrhh = buscar_persona(legajo), buscar_persona(RRHH)
    assert usuario and rrhh
    solicitud = enviar(usuario, crear_borrador(usuario, cuerpo).id)
    auditar(solicitud, rrhh, "sistema", "sembrar", EstadoSolicitud.APROBADA, solicitud.creada_en)
    sesion.commit()
    return solicitud.id


def test_solo_rrhh(como, aprobadas):
    for url in ("/api/exportaciones/pendientes", "/api/exportaciones"):
        assert como(1001).get(url).status_code == 403
    assert como(2001).post("/api/exportaciones", json={"solicitudes": aprobadas}).status_code == 403


def test_pendientes_son_las_aprobadas(como, aprobadas):
    pendientes = como(RRHH).get("/api/exportaciones/pendientes").get_json()
    assert len(pendientes) == 5
    assert {p["estado"] for p in pendientes} == {"APROBADA"}


def test_exportar_crea_el_lote_y_marca_exportadas(como, aprobadas):
    respuesta = como(RRHH).post("/api/exportaciones", json={"solicitudes": aprobadas})
    assert respuesta.status_code == 201
    lote = respuesta.get_json()
    # 26+28, 41, 38+28+28, 40, 37+37
    assert (lote["cantidad_filas"], lote["cantidad_solicitudes"]) == (9, 5)
    hoy = hoy_negocio()
    assert (lote["anio_novedad"], lote["mes_novedad"]) == (hoy.year, hoy.month)
    assert lote["nombre_archivo"].startswith("Novedades_GMS_")

    assert como(RRHH).get("/api/exportaciones/pendientes").get_json() == []
    detalle = como(RRHH).get(f"/api/solicitudes/{aprobadas[0]}").get_json()
    assert detalle["estado"] == "EXPORTADA" and detalle["lote_exportacion_id"] == lote["id"]
    assert detalle["auditoria"][-1]["accion"] == "exportar"
    assert [lote_listado["id"] for lote_listado in como(RRHH).get("/api/exportaciones").get_json()] == [
        lote["id"]
    ]


def test_no_se_exporta_dos_veces(como, aprobadas):
    como(RRHH).post("/api/exportaciones", json={"solicitudes": aprobadas})
    respuesta = como(RRHH).post("/api/exportaciones", json={"solicitudes": aprobadas[:1]})
    assert respuesta.status_code == 409
    assert respuesta.get_json()["codigo"] == "NO_EXPORTABLE"


def test_el_excel_se_puede_volver_a_bajar_identico(como, aprobadas):
    lote = como(RRHH).post("/api/exportaciones", json={"solicitudes": aprobadas}).get_json()
    url = f"/api/exportaciones/{lote['id']}/excel"
    primera, segunda = como(RRHH).get(url), como(RRHH).get(url)
    assert primera.status_code == 200
    assert primera.headers["Content-Disposition"].endswith(lote["nombre_archivo"])
    hoja = load_workbook(BytesIO(primera.data)).active
    hoja_otra = load_workbook(BytesIO(segunda.data)).active
    assert hoja.title == "Novedades a cargar"
    assert hoja.max_row == 1 + lote["cantidad_filas"]
    valores = [[c.value for c in fila] for fila in hoja.iter_rows()]
    assert valores == [[c.value for c in fila] for fila in hoja_otra.iter_rows()]
    assert [fila[1] for fila in valores[1:]] == [26, 28, 41, 38, 28, 28, 40, 37, 37]


def test_una_fila_invalida_bloquea_todo_el_lote(como, aprobadas):
    # Observaciones de más de 250 caracteres: GMS no las acepta (§7.4).
    invalida = _aprobar_retiro_con_motivo("x" * 300)
    respuesta = como(RRHH).post("/api/exportaciones", json={"solicitudes": [*aprobadas, invalida]})
    assert respuesta.status_code == 422
    assert {e["campo"] for e in respuesta.get_json()["errores"]} == {f"solicitudes.{invalida}"}
    assert len(como(RRHH).get("/api/exportaciones/pendientes").get_json()) == 6
    assert como(RRHH).get("/api/exportaciones").get_json() == []


def test_pedidos_invalidos(como, aprobadas):
    assert como(RRHH).post("/api/exportaciones", json={"solicitudes": []}).status_code == 422
    assert como(RRHH).post("/api/exportaciones", json={"solicitudes": ["1"]}).status_code == 400
    assert como(RRHH).post("/api/exportaciones", json={"solicitudes": [999_999]}).status_code == 409
    assert como(RRHH).get("/api/exportaciones/999999/excel").status_code == 404


def test_anio_y_mes_salen_de_la_fecha_de_exportacion(db, aprobadas):
    rrhh = buscar_persona(RRHH)
    assert rrhh
    ahora = datetime(2027, 1, 5, 10, 30, tzinfo=ZONA_NEGOCIO)
    lote = servicio.exportar(rrhh, aprobadas, ahora)
    assert (lote.anio_novedad, lote.mes_novedad) == (2027, 1)
    assert {(n.anio_novedad, n.mes_novedad) for n in lote.novedades} == {(2027, 1)}
    assert lote.nombre_archivo == "Novedades_GMS_20270105-1030.xlsx"
    assert sesion.get(Solicitud, aprobadas[0]).estado == EstadoSolicitud.EXPORTADA  # type: ignore[union-attr]
