import pytest

from app.errores import ErrorValidacion
from app.identidad import buscar_persona
from app.modelos import EstadoSolicitud, Solicitud, TipoSolicitud
from app.solicitudes.circuito import acciones_disponibles, validar_motivo
from app.solicitudes.visibilidad import estado_visible

E = EstadoSolicitud


def _solicitud(estado: EstadoSolicitud, solicitante: int = 1001) -> Solicitud:
    return Solicitud(
        tipo=TipoSolicitud.CAMBIO_TURNO,
        estado=estado,
        solicitante_legajo=solicitante,
        solicitante_nombre="X",
        jefe_legajo=2001,
        companero_legajo=1002,
    )


def _acciones(legajo: int, solicitud: Solicitud) -> list[str]:
    usuario = buscar_persona(legajo)
    assert usuario
    return list(acciones_disponibles(usuario, solicitud))


@pytest.mark.parametrize(
    ("estado", "con_paso"),
    [
        (E.PENDIENTE_COMPANERO, {1002}),
        (E.PENDIENTE_JEFE, {2001}),
        (E.PENDIENTE_RRHH, {3001}),
        (E.BORRADOR, set()),
        (E.APROBADA, set()),
        (E.RECHAZADA, set()),
        (E.EXPORTADA, set()),
    ],
)
def test_quien_tiene_el_paso(estado, con_paso):
    solicitud = _solicitud(estado)
    for legajo in (1001, 1002, 1003, 2001, 2002, 3001):
        esperado = ["aprobar", "rechazar"] if legajo in con_paso else []
        assert _acciones(legajo, solicitud) == esperado, legajo


def test_rrhh_no_aprueba_su_propia_solicitud():
    assert _acciones(3001, _solicitud(E.PENDIENTE_RRHH, solicitante=3001)) == []


def test_motivo_de_rechazo():
    assert validar_motivo("  Falta personal  ") == "Falta personal"
    for invalido in (None, "", "  no ", 123, "x" * 501):
        with pytest.raises(ErrorValidacion):
            validar_motivo(invalido)


@pytest.mark.parametrize(
    ("estado", "para_el_resto"),
    [
        (E.APROBADA, "NO_CARGADA"),
        (E.ERROR_CARGA, "NO_CARGADA"),
        (E.EXPORTADA, "CARGADA"),
        (E.CARGADA_GMS, "CARGADA"),
        (E.PENDIENTE_JEFE, "PENDIENTE_JEFE"),
        (E.RECHAZADA, "RECHAZADA"),
    ],
)
def test_estado_visible(estado, para_el_resto):
    assert estado_visible(estado, todo=False) == para_el_resto
    assert estado_visible(estado, todo=True) == estado.value
