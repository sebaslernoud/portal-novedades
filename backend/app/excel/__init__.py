"""Excel de carga masiva de GMS: 16 columnas, una sola hoja "Novedades a cargar".

Port de src/excel/generarExcel.js de proyecto-auto-sc (docs/REGLAS-DE-NEGOCIO.md, sección 12).
"""

from app.excel.generar import generar_excel, nombre_archivo
from app.excel.validar import ErrorValidacion, separar_validas, validar_fila

__all__ = ["ErrorValidacion", "generar_excel", "nombre_archivo", "separar_validas", "validar_fila"]
