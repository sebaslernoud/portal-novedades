// Cliente de la API del backend. Todas las rutas cuelgan de /api (en desarrollo, Vite las
// redirige al contenedor del backend).

export type EstadoSalud = {
  estado: 'ok' | 'error';
  base_de_datos: string;
  migracion?: string;
};

export async function obtenerSalud(): Promise<EstadoSalud> {
  const respuesta = await fetch('/api/salud');
  if (!respuesta.ok && respuesta.status !== 503) {
    throw new Error(`El backend respondió ${respuesta.status}`);
  }
  return respuesta.json() as Promise<EstadoSalud>;
}
