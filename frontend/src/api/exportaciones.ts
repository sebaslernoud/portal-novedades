import { descargar, pedir } from './cliente';
import type { Lote, Solicitud } from './tipos';

export const listarPendientesDeExportar = () => pedir<Solicitud[]>('/exportaciones/pendientes');

export const listarLotes = () => pedir<Lote[]>('/exportaciones');

export const exportar = (solicitudes: number[]) => pedir<Lote>('/exportaciones', 'POST', { solicitudes });

export const descargarExcel = (lote: Lote) => descargar(`/exportaciones/${lote.id}/excel`, lote.nombre_archivo);
