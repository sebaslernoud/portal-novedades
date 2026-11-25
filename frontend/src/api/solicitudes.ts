import { pedir } from './cliente';
import type { Bandeja, CuerpoSolicitud, FilaGms, ListaSolicitudes, Previsualizacion, Solicitud } from './tipos';

export const obtenerBandeja = () => pedir<Bandeja>('/bandeja');

export const aprobarSolicitud = (id: number) => pedir<Solicitud>(`/solicitudes/${id}/aprobar`, 'POST');

export const rechazarSolicitud = (id: number, motivo: string) =>
  pedir<Solicitud>(`/solicitudes/${id}/rechazar`, 'POST', { motivo });

export const obtenerNovedadesPrevistas = (id: number) => pedir<FilaGms[]>(`/solicitudes/${id}/novedades`);

export const previsualizar = (cuerpo: CuerpoSolicitud) =>
  pedir<Previsualizacion>('/solicitudes/previsualizar', 'POST', cuerpo);

export const crearBorrador = (cuerpo: CuerpoSolicitud) => pedir<Solicitud>('/solicitudes', 'POST', cuerpo);

export const editarBorrador = (id: number, cuerpo: CuerpoSolicitud) =>
  pedir<Solicitud>(`/solicitudes/${id}`, 'PUT', cuerpo);

export const enviarSolicitud = (id: number) => pedir<Solicitud>(`/solicitudes/${id}/enviar`, 'POST');

export const listarSolicitudes = () => pedir<ListaSolicitudes>('/solicitudes');

export const obtenerSolicitud = (id: number) => pedir<Solicitud>(`/solicitudes/${id}`);
