"""Casos heredados de proyecto-auto-sc (docs/casos-de-prueba-reglas.json) y su adaptador.

Convierte la entrada del motor original (fechas dd/mm/aaaa, legajo como texto) a la solicitud
tipada del portal, y las filas del portal a la forma de `filasEsperadas`.
"""

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

from app.reglas.entradas import (
    CambioTurno,
    FrancoAutorizado,
    FrancoCompensatorio,
    LicenciaEspecial,
    Persona,
    Renglon,
    RetiroIngreso,
    Solicitud,
    Vacaciones,
)
from app.reglas.fechas import formatear
from app.reglas.fila import FilaNovedad

HOY = date(2026, 11, 24)


def ruta_docs() -> Path:
    # Local: backend/tests → raíz del repo. En Docker, docs/ se monta en /docs.
    local = Path(__file__).resolve().parents[2] / "docs"
    return local if local.exists() else Path("/docs")


def _ruta_casos() -> Path:
    if os.environ.get("CASOS_REGLAS"):
        return Path(os.environ["CASOS_REGLAS"])
    return ruta_docs() / "casos-de-prueba-reglas.json"


CASOS: list[dict[str, Any]] = json.loads(_ruta_casos().read_text(encoding="utf-8"))["casos"]


# --- Adaptador ---------------------------------------------------------------------------------


def _fecha(texto: str | None) -> date | None:
    return datetime.strptime(texto, "%d/%m/%Y").date() if texto else None


def _persona(entrada: dict[str, Any], rol: str) -> Persona | None:
    for p in entrada.get("personas", []):
        if p["rol"] == rol:
            legajo = p.get("legajoTexto")
            return Persona(legajo=int(legajo) if legajo else None, nombre=p.get("nombre"))
    return None


def _renglones(lista: list[dict[str, Any]]) -> list[Renglon]:
    return [Renglon(_fecha(r.get("fecha")), r.get("horaDesde"), r.get("horaHasta")) for r in lista]


def a_solicitud(caso: dict[str, Any]) -> Solicitud:
    e = caso["entrada"]
    titular = _persona(e, "titular")
    match caso["tipoFormulario"]:
        case "retiro_ingreso_fuera_horario":
            r = e["retiroIngreso"]
            return RetiroIngreso(
                persona=titular,
                tipo="ingreso" if r["opcionMarcada"] == "ingresar" else "retiro",
                fecha=_fecha(r["fecha"]),
                hora=r["hora"],
                horario_laboral_desde=r["horarioLaboralDesde"],
                horario_laboral_hasta=r["horarioLaboralHasta"],
                motivo=r["motivo"],
                devoluciones=_renglones(r["devoluciones"]),
            )
        case "licencia_especial":
            lic = e["licenciaEspecial"]
            return LicenciaEspecial(
                persona=titular,
                tipo_licencia=lic["tipoLicencia"],
                fecha_desde=_fecha(lic["fechaDesde"]),
                fecha_hasta=_fecha(lic["fechaHasta"]),
                fecha_reintegro=_fecha(lic["fechaReintegro"]),
                cantidad_dias=lic["cantidadDiasNumero"],
                motivo=lic["motivoTexto"],
            )
        case "franco_compensatorio":
            f = e["francoCompensatorio"]
            return FrancoCompensatorio(
                persona=titular,
                fecha_franco=_fecha(f["fechaFranco"]),
                hora_desde_franco=f["horaDesdeFranco"],
                hora_hasta_franco=f["horaHastaFranco"],
                franco_a_determinar=f["francoADeterminar"],
                dias_trabajados=_renglones(f["diasTrabajados"]),
                motivo=f["motivo"],
            )
        case "franco_autorizado":
            f = e["francoAutorizado"]
            return FrancoAutorizado(
                persona=titular, fecha_franco=_fecha(f["fechaFranco"]), motivo=f["motivo"]
            )
        case "cambio_turno":
            c = e["cambioTurno"]
            return CambioTurno(
                solicitante=_persona(e, "solicitante"),
                aceptante=_persona(e, "aceptante"),
                fecha_cambio=_fecha(c["fechaCambio"]),
                fecha_devolucion=_fecha(c["fechaDevolucion"]),
            )
        case "comunicacion_vacacional":
            v = e["vacaciones"]
            return Vacaciones(
                persona=titular,
                fecha_desde=_fecha(v["fechaDesde"]),
                fecha_hasta=_fecha(v["fechaHasta"]),
                fecha_reintegro=_fecha(v["fechaReintegro"]),
                cantidad_dias=v["cantidadDiasNumero"],
            )
    raise ValueError(f"Tipo de formulario sin adaptador: {caso['tipoFormulario']}")


def fila_como_en_el_caso(fila: FilaNovedad) -> dict[str, Any]:
    """Misma forma y orden de campos que `filasEsperadas`."""

    def f(valor: date | None) -> str | None:
        return formatear(valor) if valor else None

    return {
        "legajo": fila.legajo,
        "concepto": fila.concepto,
        "cantidad": fila.cantidad,
        "fechaDesde": f(fila.fecha_desde),
        "fechaHasta": f(fila.fecha_hasta),
        "observaciones": fila.observaciones,
        "anioNovedad": fila.anio_novedad,
        "mesNovedad": fila.mes_novedad,
        "fechaValidarFichadas": f(fila.fecha_validar_fichadas),
        "fechaNov28": f(fila.fecha_nov28),
        "horaDesde": fila.hora_desde,
        "horaHasta": fila.hora_hasta,
        "codigoFuturo": fila.codigo_futuro,
        "motivos": fila.motivos,
    }
