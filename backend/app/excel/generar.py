"""Excel de carga masiva para GMS (proyecto-auto-sc/src/excel/generarExcel.js).

GMS acepta una sola hoja. Las celdas sin valor no se escriben (ni "", ni 0, ni "null").
CODIGOMOTIVOHE, LEGAJOCOBERTURA y CANTIDADHE están reservadas y van siempre vacías.
"""

import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Literal

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

from app.reglas.fechas import ahora_negocio
from app.reglas.fila import FilaNovedad
from app.reglas.horas import hora_a_fraccion

NOMBRE_HOJA = "Novedades a cargar"


@dataclass(frozen=True)
class Columna:
    encabezado: str
    campo: str | None  # None: columna reservada, siempre vacía
    ancho: int
    tipo: Literal["numero", "fecha", "hora", "texto"]

    @property
    def formato(self) -> str | None:
        return {"numero": "0", "fecha": "dd/mm/yyyy", "hora": "hh:mm"}.get(self.tipo)


COLUMNAS: tuple[Columna, ...] = (
    Columna("Legajo", "legajo", 12, "numero"),
    Columna("Concepto", "concepto", 11, "numero"),
    Columna("Cantidad", "cantidad", 10, "numero"),
    Columna("FechaDesde", "fecha_desde", 14, "fecha"),
    Columna("FechaHasta", "fecha_hasta", 14, "fecha"),
    Columna("Observaciones", "observaciones", 50, "texto"),
    Columna("AnioNovedad", "anio_novedad", 13, "numero"),
    Columna("mesNovedad", "mes_novedad", 12, "numero"),
    Columna("FechaValidarFichadas", "fecha_validar_fichadas", 20, "fecha"),
    Columna("FechaNov28", "fecha_nov28", 14, "fecha"),
    Columna("HORADESDE", "hora_desde", 11, "hora"),
    Columna("HORAHASTA", "hora_hasta", 11, "hora"),
    Columna("CODIGOFUTURO", "codigo_futuro", 15, "numero"),
    Columna("CODIGOMOTIVOHE", None, 16, "numero"),
    Columna("LEGAJOCOBERTURA", None, 17, "numero"),
    Columna("CANTIDADHE", None, 12, "numero"),
)


def _valor_celda(columna: Columna, fila: FilaNovedad) -> object:
    valor = getattr(fila, columna.campo) if columna.campo else None
    if valor is None or valor == "":
        return None
    if columna.tipo == "hora":
        return hora_a_fraccion(valor)
    return valor


def generar_excel(filas: Sequence[FilaNovedad]) -> bytes:
    """Devuelve el .xlsx. Las filas tienen que venir validadas (ver app.excel.validar)."""
    libro = Workbook()
    hoja = libro.active
    hoja.title = NOMBRE_HOJA
    hoja.freeze_panes = "A2"

    negrita = Font(bold=True)
    for posicion, columna in enumerate(COLUMNAS, start=1):
        celda = hoja.cell(row=1, column=posicion, value=columna.encabezado)
        celda.font = negrita
        hoja.column_dimensions[get_column_letter(posicion)].width = columna.ancho

    for numero_fila, fila in enumerate(filas, start=2):
        for posicion, columna in enumerate(COLUMNAS, start=1):
            valor = _valor_celda(columna, fila)
            if valor is None:
                continue
            celda = hoja.cell(row=numero_fila, column=posicion, value=valor)
            if columna.formato:
                celda.number_format = columna.formato

    salida = BytesIO()
    libro.save(salida)
    return salida.getvalue()


def nombre_archivo(base: str = "GMS", instante: datetime | None = None) -> str:
    """Novedades_<base>_<aaaammdd>-<hhmm>.xlsx, con la hora de Buenos Aires."""
    limpia = re.sub(r"[^a-zA-Z0-9]", "_", base)[:40]
    momento = instante or ahora_negocio()
    return f"Novedades_{limpia}_{momento:%Y%m%d-%H%M}.xlsx"
