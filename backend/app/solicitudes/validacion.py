"""Validación de lo que manda el formulario web y conversión a la entrada del motor de reglas.

Solo bloquea lo que la especificación marca como obligatorio o con formato inválido (§4). La
coherencia (horas que no cierran, topes, etc.) no se valida acá: son advertencias.
"""

import re
from dataclasses import dataclass
from datetime import date
from typing import Any

from app.errores import ErrorApi, ErrorCampo, ErrorValidacion
from app.identidad import Usuario, buscar_persona
from app.modelos import TipoSolicitud
from app.reglas.constantes import MAX_RENGLONES_DEVOLUCION, TIPOS_LICENCIA_LEGIBLES
from app.reglas.entradas import (
    CambioTurno,
    FrancoAutorizado,
    FrancoCompensatorio,
    LicenciaEspecial,
    Persona,
    Renglon,
    RetiroIngreso,
)
from app.reglas.entradas import Solicitud as EntradaReglas

MAX_TEXTO = 500
_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_HORA = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")

COMPLETAR = "Completá este campo."


@dataclass(frozen=True)
class Borrador:
    tipo: TipoSolicitud
    jefe_legajo: int | None
    comentario: str | None
    datos: dict[str, Any]


@dataclass(frozen=True)
class SolicitudValidada:
    tipo: TipoSolicitud
    entrada: EntradaReglas
    jefe: Usuario
    companero: Usuario | None
    comentario: str | None
    # Solo los campos del formulario, con formato canónico (fechas ISO, horas HH:MM).
    datos: dict[str, Any]


class _Validador:
    def __init__(self, datos: dict[str, Any]) -> None:
        self.datos = datos
        self.errores: list[ErrorCampo] = []
        self.normalizados: dict[str, Any] = {}

    def error(self, campo: str, mensaje: str) -> None:
        self.errores.append(ErrorCampo(campo, mensaje))

    def _valor(self, origen: dict[str, Any], clave: str) -> Any:
        valor = origen.get(clave)
        return None if valor is None or (isinstance(valor, str) and valor.strip() == "") else valor

    def fecha(
        self, clave: str, obligatoria: bool, origen: dict[str, Any] | None = None, campo: str | None = None
    ) -> date | None:
        campo = campo or f"datos.{clave}"
        valor = self._valor(self.datos if origen is None else origen, clave)
        if valor is None:
            if obligatoria:
                self.error(campo, COMPLETAR)
            return None
        try:
            if not isinstance(valor, str) or not _FECHA.match(valor):
                raise ValueError
            resultado = date.fromisoformat(valor)
        except ValueError:
            self.error(campo, "Fecha inválida.")
            return None
        if origen is None:
            self.normalizados[clave] = resultado.isoformat()
        return resultado

    def hora(
        self, clave: str, obligatoria: bool, origen: dict[str, Any] | None = None, campo: str | None = None
    ) -> str | None:
        campo = campo or f"datos.{clave}"
        valor = self._valor(self.datos if origen is None else origen, clave)
        if valor is None:
            if obligatoria:
                self.error(campo, COMPLETAR)
            return None
        if not isinstance(valor, str) or not _HORA.match(valor):
            self.error(campo, "Hora inválida: usar HH:MM.")
            return None
        if origen is None:
            self.normalizados[clave] = valor
        return valor

    def texto(self, clave: str, obligatorio: bool) -> str | None:
        campo = f"datos.{clave}"
        valor = self._valor(self.datos, clave)
        if valor is None:
            if obligatorio:
                self.error(campo, COMPLETAR)
            return None
        if not isinstance(valor, str):
            self.error(campo, "Texto inválido.")
            return None
        valor = valor.strip()
        if len(valor) > MAX_TEXTO:
            self.error(campo, f"Máximo {MAX_TEXTO} caracteres.")
            return None
        self.normalizados[clave] = valor
        return valor

    def opcion(self, clave: str, opciones: set[str]) -> str | None:
        valor = self._valor(self.datos, clave)
        if valor is None:
            self.error(f"datos.{clave}", COMPLETAR)
            return None
        if valor not in opciones:
            self.error(f"datos.{clave}", "Elegí una opción de la lista.")
            return None
        self.normalizados[clave] = valor
        return valor

    def booleano(self, clave: str) -> bool:
        valor = bool(self.datos.get(clave, False))
        self.normalizados[clave] = valor
        return valor

    def entero(self, clave: str) -> int | None:
        valor = self.datos.get(clave)
        if valor is None or valor == "":
            self.error(f"datos.{clave}", COMPLETAR)
            return None
        if not isinstance(valor, int) or isinstance(valor, bool):
            self.error(f"datos.{clave}", "Valor inválido.")
            return None
        self.normalizados[clave] = valor
        return valor

    def renglones(self, clave: str) -> list[Renglon]:
        lista = self.datos.get(clave) or []
        if not isinstance(lista, list):
            self.error(f"datos.{clave}", "Formato inválido.")
            return []
        if len(lista) > MAX_RENGLONES_DEVOLUCION:
            self.error(f"datos.{clave}", f"Máximo {MAX_RENGLONES_DEVOLUCION} renglones.")
            return []
        renglones: list[Renglon] = []
        normalizados: list[dict[str, str]] = []
        for i, item in enumerate(lista):
            prefijo = f"datos.{clave}.{i}"
            if not isinstance(item, dict):
                self.error(prefijo, "Formato inválido.")
                continue
            # Si hay renglón, sus tres datos son obligatorios.
            fecha = self.fecha("fecha", True, item, f"{prefijo}.fecha")
            desde = self.hora("hora_desde", True, item, f"{prefijo}.hora_desde")
            hasta = self.hora("hora_hasta", True, item, f"{prefijo}.hora_hasta")
            if fecha and desde and hasta:
                renglones.append(Renglon(fecha, desde, hasta))
                normalizados.append({"fecha": fecha.isoformat(), "hora_desde": desde, "hora_hasta": hasta})
        self.normalizados[clave] = normalizados
        return renglones


def validar_borrador(cuerpo: Any) -> Borrador:
    """Un borrador puede estar incompleto: solo se controla la forma general."""
    if not isinstance(cuerpo, dict):
        raise ErrorApi("CUERPO_INVALIDO", "El pedido no tiene el formato esperado.", 400)
    errores: list[ErrorCampo] = []
    try:
        tipo = TipoSolicitud(cuerpo.get("tipo"))
    except ValueError:
        errores.append(ErrorCampo("tipo", "Elegí un tipo de formulario."))
    jefe = cuerpo.get("jefe_legajo")
    if jefe is not None and (not isinstance(jefe, int) or isinstance(jefe, bool)):
        errores.append(ErrorCampo("jefe_legajo", "Valor inválido."))
    comentario = cuerpo.get("comentario")
    if comentario is not None and (not isinstance(comentario, str) or len(comentario.strip()) > MAX_TEXTO):
        errores.append(ErrorCampo("comentario", f"Máximo {MAX_TEXTO} caracteres."))
    datos = cuerpo.get("datos", {})
    if not isinstance(datos, dict):
        errores.append(ErrorCampo("datos", "Formato inválido."))
    if errores:
        raise ErrorValidacion(errores)
    comentario = comentario.strip() if isinstance(comentario, str) else None
    return Borrador(tipo, jefe, comentario or None, datos)


def validar_envio(solicitante: Usuario, borrador: Borrador) -> SolicitudValidada:
    """Valida todo lo obligatorio y arma la entrada del motor. El solicitante es el usuario actual."""
    v = _Validador(borrador.datos)
    persona = Persona(solicitante.legajo, solicitante.nombre)
    companero: Usuario | None = None
    entrada: EntradaReglas | None = None

    match borrador.tipo:
        case TipoSolicitud.RETIRO_INGRESO:
            tipo = v.opcion("tipo_movimiento", {"retiro", "ingreso"})
            entrada = RetiroIngreso(
                persona=persona,
                tipo="ingreso" if tipo == "ingreso" else "retiro",
                fecha=v.fecha("fecha", True),
                hora=v.hora("hora", True),
                horario_laboral_desde=v.hora("horario_laboral_desde", True),
                horario_laboral_hasta=v.hora("horario_laboral_hasta", True),
                motivo=v.texto("motivo", True),
                devoluciones=v.renglones("devoluciones"),
            )
        case TipoSolicitud.LICENCIA_ESPECIAL:
            entrada = LicenciaEspecial(
                persona=persona,
                tipo_licencia=v.opcion("tipo_licencia", set(TIPOS_LICENCIA_LEGIBLES)),
                fecha_desde=v.fecha("fecha_desde", True),
                fecha_hasta=v.fecha("fecha_hasta", True),
                fecha_reintegro=v.fecha("fecha_reintegro", False),
            )
            # El detalle es para RR.HH. y no va a GMS: no entra al motor.
            v.texto("detalle", False)
        case TipoSolicitud.FRANCO_COMPENSATORIO:
            a_determinar = v.booleano("franco_a_determinar")
            fecha_franco = v.fecha("fecha_franco", not a_determinar)
            renglones = v.renglones("dias_trabajados")
            if fecha_franco is None and not renglones and not v.errores:
                v.error("datos.dias_trabajados", "Cargá la fecha del franco o al menos un día trabajado.")
            entrada = FrancoCompensatorio(
                persona=persona,
                fecha_franco=fecha_franco,
                hora_desde_franco=v.hora("hora_desde_franco", fecha_franco is not None),
                hora_hasta_franco=v.hora("hora_hasta_franco", fecha_franco is not None),
                franco_a_determinar=a_determinar,
                dias_trabajados=renglones,
                motivo=v.texto("motivo", False),
            )
        case TipoSolicitud.FRANCO_AUTORIZADO:
            entrada = FrancoAutorizado(
                persona=persona, fecha_franco=v.fecha("fecha_franco", True), motivo=v.texto("motivo", False)
            )
        case TipoSolicitud.CAMBIO_TURNO:
            legajo = v.entero("companero_legajo")
            if legajo is not None:
                companero = buscar_persona(legajo)
                if companero is None:
                    v.error("datos.companero_legajo", "No encontramos a ese compañero.")
                elif companero.legajo == solicitante.legajo:
                    v.error("datos.companero_legajo", "No podés elegirte a vos mismo como compañero.")
                    companero = None
            entrada = CambioTurno(
                solicitante=persona,
                aceptante=Persona(companero.legajo, companero.nombre) if companero else None,
                fecha_cambio=v.fecha("fecha_cambio", True),
                fecha_devolucion=v.fecha("fecha_devolucion", True),
            )

    jefe = _validar_jefe(v, borrador.jefe_legajo, solicitante, companero)
    if v.errores or entrada is None or jefe is None:
        raise ErrorValidacion(v.errores)
    return SolicitudValidada(borrador.tipo, entrada, jefe, companero, borrador.comentario, v.normalizados)


def _validar_jefe(
    v: _Validador, legajo: int | None, solicitante: Usuario, companero: Usuario | None
) -> Usuario | None:
    if legajo is None:
        v.error("jefe_legajo", "Elegí el jefe que aprueba.")
        return None
    jefe = buscar_persona(legajo)
    if jefe is None or not jefe.tiene_rol("jefe"):
        v.error("jefe_legajo", "Elegí un jefe de la lista.")
        return None
    if jefe.legajo == solicitante.legajo:
        v.error("jefe_legajo", "No podés elegirte a vos mismo como jefe.")
        return None
    if companero and jefe.legajo == companero.legajo:
        v.error("jefe_legajo", "El jefe no puede ser el compañero del cambio de turno.")
        return None
    return jefe
