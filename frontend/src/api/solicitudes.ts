import { pedir } from './cliente';
import type { CuerpoSolicitud, ListaSolicitudes, Previsualizacion, Solicitud } from './tipos';

export const previsualizar = (cuerpo: CuerpoSolicitud) =>
  pedir<Previsualizacion>('/solicitudes/previsualizar', 'POST', cuerpo);

export const crearBorrador = (cuerpo: CuerpoSolicitud) => pedir<Solicitud>('/solicitudes', 'POST', cuerpo);

export const editarBorrador = (id: number, cuerpo: CuerpoSolicitud) =>
  pedir<Solicitud>(`/solicitudes/${id}`, 'PUT', cuerpo);

export const enviarSolicitud = (id: number) => pedir<Solicitud>(`/solicitudes/${id}/enviar`, 'POST');

export const listarSolicitudes = () => pedir<ListaSolicitudes>('/solicitudes');

export const obtenerSolicitud = (id: number) => pedir<Solicitud>(`/solicitudes/${id}`);
