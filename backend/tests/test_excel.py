"""Excel para GMS: tiene que reproducir docs/Ejemplo-salida-GMS.xlsx, generado con el motor original."""

from dataclasses import replace
from datetime import date, datetime
from io import BytesIO

import pytest
from casos_heredados import CASOS, HOY, a_solicitud, ruta_docs
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

from app.excel import generar_excel, nombre_archivo, separar_validas, validar_fila
from app.excel.generar import COLUMNAS, NOMBRE_HOJA
from app.reglas import FilaNovedad, generar_filas


def _filas_sin_advertencias() -> list[FilaNovedad]:
    """El ejemplo de referencia tiene las filas de los casos que no traen advertencias, en orden."""
    filas = [f for caso in CASOS for f in generar_filas(a_solicitud(caso), hoy=HOY)]
    return [f for f in filas if not f.motivos]


def _ancho(hoja, columna: int) -> float:
    """openpyxl agrupa columnas contiguas del mismo ancho en un solo rango (ej. D:E)."""
    letra = get_column_letter(columna)
    for dimension in hoja.column_dimensions.values():
        if dimension.min <= columna <= dimension.max:
            return dimension.width
    return hoja.column_dimensions[letra].width


@pytest.fixture(scope="module")
def generado():
    return load_workbook(BytesIO(generar_excel(_filas_sin_advertencias())))


@pytest.fixture(scope="module")
def referencia():
    return load_workbook(ruta_docs() / "Ejemplo-salida-GMS.xlsx")


def test_una_sola_hoja_con_encabezados_fijos(generado):
    assert generado.sheetnames == [NOMBRE_HOJA]
    hoja = generado.active
    assert hoja.freeze_panes == "A2"
    assert [c.value for c in hoja[1]] == [c.encabezado for c in COLUMNAS]
    assert all(c.font.b for c in hoja[1])


def test_igual_al_ejemplo_de_referencia(generado, referencia):
    hoja = generado.active
    ref = referencia.active
    assert ref.title == hoja.title
    assert (hoja.max_row, hoja.max_column) == (ref.max_row, ref.max_column)
    for columna in range(1, ref.max_column + 1):
        assert _ancho(hoja, columna) == _ancho(ref, columna), get_column_letter(columna)
    for fila_ref, fila in zip(ref.iter_rows(), hoja.iter_rows(), strict=True):
        for celda_ref, celda in zip(fila_ref, fila, strict=True):
            esperado = (celda_ref.value, celda_ref.data_type, celda_ref.number_format)
            assert (celda.value, celda.data_type, celda.number_format) == esperado, celda.coordinate


def test_celdas_vacias_no_se_escriben(generado):
    hoja = generado.active
    for fila in hoja.iter_rows(min_row=2):
        for celda in fila:
            assert celda.value not in ("", 0, "null")
    # Las columnas reservadas van siempre vacías.
    for columna in range(14, 17):
        assert all(hoja.cell(row=r, column=columna).value is None for r in range(2, hoja.max_row + 1))


def test_horas_como_fraccion_de_dia():
    fila = FilaNovedad(
        legajo=1, concepto=28, cantidad=1, fecha_desde=date(2026, 11, 27), fecha_hasta=date(2026, 11, 27),
        anio_novedad=2026, mes_novedad=11, hora_desde="18:00", hora_hasta="20:30",
    )  # fmt: skip
    libro = load_workbook(BytesIO(generar_excel([fila])))
    hoja = libro.active
    assert hoja["L2"].number_format == "hh:mm"
    # openpyxl devuelve la fracción de día como hora; 20:30 → 0.854166… del día.
    assert (hoja["K2"].value.hour, hoja["K2"].value.minute) == (18, 0)
    assert (hoja["L2"].value.hour, hoja["L2"].value.minute) == (20, 30)


def _fila_valida() -> FilaNovedad:
    return FilaNovedad(
        legajo=1234, concepto=40, cantidad=1, fecha_desde=date(2026, 12, 2),
        fecha_hasta=date(2026, 12, 2), observaciones="Franco autorizado.", anio_novedad=2026, mes_novedad=11,
    )  # fmt: skip


def test_fila_valida_pasa_la_validacion():
    assert validar_fila(_fila_valida()) == []


@pytest.mark.parametrize(
    ("cambio", "campo"),
    [
        ({"legajo": 0}, "legajo"),
        ({"legajo": 100_000_000}, "legajo"),
        ({"concepto": 99}, "concepto"),
        ({"cantidad": 1000}, "cantidad"),
        ({"anio_novedad": 1999}, "anio_novedad"),
        ({"mes_novedad": 13}, "mes_novedad"),
        ({"codigo_futuro": 10_000}, "codigo_futuro"),
        ({"hora_desde": "25:00"}, "hora_desde"),
        ({"hora_hasta": "8:00"}, "hora_hasta"),
        ({"observaciones": "x" * 251}, "observaciones"),
    ],
)
def test_validacion_de_rangos(cambio, campo):
    errores = validar_fila(replace(_fila_valida(), **cambio))
    assert [e.campo for e in errores] == [campo]


def test_validacion_de_obligatorios():
    fila = replace(_fila_valida(), concepto=28, fecha_hasta=None)
    assert [e.mensaje for e in validar_fila(fila)] == ["Falta FechaHasta", "Falta HORADESDE"]


def test_las_advertencias_no_bloquean_la_exportacion():
    fila = replace(_fila_valida(), motivos=["Las horas no cierran: adeuda 2 h y devuelve 1 h, confirmar"])
    assert validar_fila(fila) == []


def test_separar_validas_descarta_las_invalidas():
    invalida = replace(_fila_valida(), legajo=None)
    validas, errores = separar_validas([_fila_valida(), invalida])
    assert validas == [_fila_valida()]
    assert [(e.indice, e.mensaje) for e in errores] == [(1, "Falta el legajo")]


def test_nombre_de_archivo():
    instante = datetime(2026, 11, 24, 9, 5)
    assert nombre_archivo("Exportación RR.HH.", instante) == "Novedades_Exportaci_n_RR_HH__20261124-0905.xlsx"
    assert len(nombre_archivo("x" * 100, instante)) == len("Novedades__20261124-0905.xlsx") + 40
