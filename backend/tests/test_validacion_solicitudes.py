from copy import deepcopy
from datetime import date

import pytest

from app.cli import ejemplos
from app.errores import ErrorApi, ErrorValidacion
from app.identidad import buscar_persona
from app.reglas.entradas import (
    CambioTurno,
    FrancoAutorizado,
    FrancoCompensatorio,
    LicenciaEspecial,
    Renglon,
    RetiroIngreso,
)
from app.solicitudes.validacion import validar_borrador, validar_envio

HOY = date(2026, 11, 24)
EJEMPLOS = {cuerpo["tipo"]: (legajo, cuerpo) for legajo, cuerpo in ejemplos(HOY)}


def _validar(tipo: str, cambios: dict | None = None, **cuerpo_extra):
    legajo, cuerpo = deepcopy(EJEMPLOS[tipo])
    cuerpo["datos"].update(cambios or {})
    cuerpo.update(cuerpo_extra)
    usuario = buscar_persona(legajo)
    assert usuario
    return validar_envio(usuario, validar_borrador(cuerpo))


def _campos_con_error(tipo: str, cambios: dict | None = None, **cuerpo_extra) -> list[str]:
    with pytest.raises(ErrorValidacion) as error:
        _validar(tipo, cambios, **cuerpo_extra)
    return [e.campo for e in error.value.errores]


@pytest.mark.parametrize(
    ("tipo", "clase"),
    [
        ("retiro_ingreso", RetiroIngreso),
        ("licencia_especial", LicenciaEspecial),
        ("franco_compensatorio", FrancoCompensatorio),
        ("franco_autorizado", FrancoAutorizado),
        ("cambio_turno", CambioTurno),
    ],
)
def test_los_ejemplos_validos_pasan(tipo, clase):
    validada = _validar(tipo)
    assert isinstance(validada.entrada, clase)
    assert validada.jefe.tiene_rol("jefe")


def test_el_solicitante_sale_del_usuario_no_del_cuerpo():
    validada = _validar("franco_autorizado", {"legajo": 9999})
    assert validada.entrada.persona.legajo == 1004  # type: ignore[union-attr]
    assert "legajo" not in validada.datos


def test_retiro_ingreso_obligatorios():
    vacios = {c: None for c in ("tipo_movimiento", "fecha", "hora", "horario_laboral_hasta", "motivo")}
    assert _campos_con_error("retiro_ingreso", vacios) == [
        "datos.tipo_movimiento",
        "datos.fecha",
        "datos.hora",
        "datos.horario_laboral_hasta",
        "datos.motivo",
    ]


def test_renglon_incompleto_y_maximo_de_renglones():
    incompleto = [{"fecha": "2026-11-27", "hora_desde": "18:00"}]
    assert _campos_con_error("retiro_ingreso", {"devoluciones": incompleto}) == [
        "datos.devoluciones.0.hora_hasta"
    ]
    cinco = [{"fecha": "2026-11-27", "hora_desde": "18:00", "hora_hasta": "19:00"}] * 5
    assert _campos_con_error("retiro_ingreso", {"devoluciones": cinco}) == ["datos.devoluciones"]


def test_formatos_invalidos():
    errores = _campos_con_error("retiro_ingreso", {"fecha": "25/11/2026", "hora": "16hs"})
    assert errores == ["datos.fecha", "datos.hora"]


def test_licencia_tipo_de_la_lista_y_hasta_obligatoria():
    assert _campos_con_error("licencia_especial", {"tipo_licencia": "otra", "fecha_hasta": ""}) == [
        "datos.tipo_licencia",
        "datos.fecha_hasta",
    ]


def test_franco_compensatorio_condicionales():
    # Con fecha de franco, las horas del franco son obligatorias.
    assert _campos_con_error("franco_compensatorio", {"hora_desde_franco": None}) == [
        "datos.hora_desde_franco"
    ]
    # "A determinar" hace opcional la fecha, pero tiene que haber algún día trabajado.
    sin_nada = {"franco_a_determinar": True, "fecha_franco": None, "dias_trabajados": []}
    assert _campos_con_error("franco_compensatorio", sin_nada) == ["datos.dias_trabajados"]
    solo_dias = {"franco_a_determinar": True, "fecha_franco": None, "hora_desde_franco": None}
    validada = _validar("franco_compensatorio", {**solo_dias, "hora_hasta_franco": None})
    assert validada.entrada.dias_trabajados == [  # type: ignore[union-attr]
        Renglon(date(2026, 11, 20), "18:00", "20:00"),
        Renglon(date(2026, 11, 21), "18:00", "20:00"),
    ]
    # Sin "a determinar", la fecha del franco es obligatoria.
    assert _campos_con_error("franco_compensatorio", {"fecha_franco": None}) == ["datos.fecha_franco"]


def test_cambio_de_turno_compañero_y_jefe():
    assert _campos_con_error("cambio_turno", {"companero_legajo": 1001}) == ["datos.companero_legajo"]
    assert _campos_con_error("cambio_turno", {"companero_legajo": 4242}) == ["datos.companero_legajo"]
    assert _campos_con_error("cambio_turno", {"companero_legajo": 2001}) == ["jefe_legajo"]


def test_jefe_obligatorio_de_la_lista_y_distinto_del_solicitante():
    assert _campos_con_error("franco_autorizado", jefe_legajo=None) == ["jefe_legajo"]
    assert _campos_con_error("franco_autorizado", jefe_legajo=1002) == ["jefe_legajo"]
    with pytest.raises(ErrorValidacion) as error:
        cuerpo = {**EJEMPLOS["franco_autorizado"][1], "jefe_legajo": 2001}
        validar_envio(buscar_persona(2001), validar_borrador(cuerpo))  # type: ignore[arg-type]
    assert [e.mensaje for e in error.value.errores] == ["No podés elegirte a vos mismo como jefe."]


def test_mensajes_en_español():
    with pytest.raises(ErrorValidacion) as error:
        _validar("franco_autorizado", {"fecha_franco": None})
    assert error.value.mensaje == "Revisá los datos marcados."
    assert error.value.errores[0].mensaje == "Completá este campo."


def test_borrador_solo_controla_la_forma():
    borrador = validar_borrador({"tipo": "licencia_especial", "datos": {}})
    assert borrador.datos == {} and borrador.jefe_legajo is None
    with pytest.raises(ErrorValidacion) as error:
        validar_borrador({"tipo": "vacaciones", "comentario": "x" * 501, "jefe_legajo": "2001"})
    assert [e.campo for e in error.value.errores] == ["tipo", "jefe_legajo", "comentario"]
    with pytest.raises(ErrorApi):
        validar_borrador(["no", "es", "un", "objeto"])
