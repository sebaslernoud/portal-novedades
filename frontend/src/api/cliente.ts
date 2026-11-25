// Cliente de la API del backend. Todas las rutas cuelgan de /api (en desarrollo, Vite las
// redirige al contenedor del backend).
import type { ErrorCampo, Errores } from './tipos';

export type EstadoSalud = {
  estado: 'ok' | 'error';
  base_de_datos: string;
  migracion?: string;
};

export class ErrorApi extends Error {
  constructor(
    readonly codigo: string,
    mensaje: string,
    readonly status: number,
    readonly errores: ErrorCampo[] = [],
  ) {
    super(mensaje);
  }

  porCampo(): Errores {
    return Object.fromEntries(this.errores.map((e) => [e.campo, e.mensaje]));
  }
}

// Mientras no haya login, el usuario elegido viaja en este header (ver backend/app/identidad.py).
const HEADER_LEGAJO = 'X-Legajo-Prueba';
const CLAVE_LEGAJO = 'portal-novedades:legajo-prueba';

export function leerLegajoPrueba(): number | null {
  try {
    const valor = window.localStorage.getItem(CLAVE_LEGAJO);
    return valor ? Number(valor) : null;
  } catch {
    return null;
  }
}

export function guardarLegajoPrueba(legajo: number | null): void {
  try {
    if (legajo === null) window.localStorage.removeItem(CLAVE_LEGAJO);
    else window.localStorage.setItem(CLAVE_LEGAJO, String(legajo));
  } catch {
    // Sin almacenamiento (modo privado): el usuario se pierde al recargar, nada más.
  }
}

function encabezados(conCuerpo: boolean): HeadersInit {
  const legajo = leerLegajoPrueba();
  return {
    ...(conCuerpo ? { 'Content-Type': 'application/json' } : {}),
    ...(legajo ? { [HEADER_LEGAJO]: String(legajo) } : {}),
  };
}

async function errorDeRespuesta(respuesta: Response): Promise<ErrorApi> {
  try {
    const cuerpo = (await respuesta.json()) as { codigo?: string; mensaje?: string; errores?: ErrorCampo[] };
    return new ErrorApi(
      cuerpo.codigo ?? 'ERROR',
      cuerpo.mensaje ?? 'Ocurrió un error inesperado.',
      respuesta.status,
      cuerpo.errores ?? [],
    );
  } catch {
    return new ErrorApi('ERROR', `El servidor respondió ${respuesta.status}.`, respuesta.status);
  }
}

export async function pedir<T>(ruta: string, metodo = 'GET', cuerpo?: unknown): Promise<T> {
  const respuesta = await fetch(`/api${ruta}`, {
    method: metodo,
    headers: encabezados(cuerpo !== undefined),
    body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo),
  });
  if (!respuesta.ok) throw await errorDeRespuesta(respuesta);
  return (await respuesta.json()) as T;
}

// Descarga un archivo con el header del usuario (un <a href> común no lo mandaría).
export async function descargar(ruta: string, nombre: string): Promise<void> {
  const respuesta = await fetch(`/api${ruta}`, { headers: encabezados(false) });
  if (!respuesta.ok) throw await errorDeRespuesta(respuesta);
  const url = URL.createObjectURL(await respuesta.blob());
  const enlace = document.createElement('a');
  enlace.href = url;
  enlace.download = nombre;
  enlace.click();
  URL.revokeObjectURL(url);
}

export async function obtenerSalud(): Promise<EstadoSalud> {
  const respuesta = await fetch('/api/salud');
  if (!respuesta.ok && respuesta.status !== 503) {
    throw new Error(`El backend respondió ${respuesta.status}`);
  }
  return respuesta.json() as Promise<EstadoSalud>;
}
