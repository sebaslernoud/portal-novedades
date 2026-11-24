"""La fila de novedad que se carga en GMS."""

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date


@dataclass
class FilaNovedad:
    legajo: int | None = None
    concepto: int | None = None
    cantidad: int | None = None
    fecha_desde: date | None = None
    fecha_hasta: date | None = None
    observaciones: str | None = None
    anio_novedad: int | None = None
    mes_novedad: int | None = None
    fecha_validar_fichadas: date | None = None
    fecha_nov28: date | None = None
    hora_desde: str | None = None
    hora_hasta: str | None = None
    codigo_futuro: int | None = None
    # Advertencias para los aprobadores. No van al Excel.
    motivos: list[str] = field(default_factory=list)
    # Interno: tramo de horas a favor (se excluye de la lista de días de la fila principal).
    a_favor: bool = field(default=False, compare=False, repr=False)


def crear_fila(hoy: date, concepto: int, cantidad: int | None = None) -> FilaNovedad:
    """AnioNovedad y mesNovedad salen de "hoy" (ver REGLAS-DE-NEGOCIO.md, 3.5)."""
    return FilaNovedad(concepto=concepto, cantidad=cantidad, anio_novedad=hoy.year, mes_novedad=hoy.month)


def agregar_motivos(fila: FilaNovedad, motivos: str | Iterable[str]) -> None:
    """Agrega sin repetir textos idénticos y respetando el orden de llegada."""
    for motivo in [motivos] if isinstance(motivos, str) else motivos:
        if motivo and motivo not in fila.motivos:
            fila.motivos.append(motivo)
