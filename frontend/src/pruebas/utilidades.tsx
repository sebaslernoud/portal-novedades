// Utilidades de prueba: API simulada sobre fetch y render de la app completa en una ruta.
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';
import { guardarLegajoPrueba } from '../api/cliente';
import type { Usuario } from '../api/tipos';
import { ProveedorUsuario } from '../contexto/Usuario';

export const PERSONAS: Usuario[] = [
  { legajo: 1001, nombre: 'JUAN PEREZ', sector: '4to piso', roles: ['empleado'] },
  { legajo: 1004, nombre: 'LUCIA FERNANDEZ', sector: 'Planta baja', roles: ['empleado'] },
  { legajo: 2001, nombre: 'MARIA LOPEZ', sector: '4to piso', roles: ['empleado', 'jefe'] },
  { legajo: 3001, nombre: 'SOFIA RAMIREZ', sector: 'RR.HH.', roles: ['empleado', 'rrhh'] },
];

type Ruta = unknown | ((cuerpo: unknown) => unknown);
export type Llamada = { clave: string; cuerpo: unknown };

export function respuesta(status: number, cuerpo: unknown): Response {
  return new Response(JSON.stringify(cuerpo), { status, headers: { 'Content-Type': 'application/json' } });
}

// rutas: { 'GET /api/solicitudes': {...}, 'POST /api/solicitudes': (cuerpo) => ... }
export function simularApi(rutas: Record<string, Ruta>): Llamada[] {
  const llamadas: Llamada[] = [];
  const todas: Record<string, Ruta> = { 'GET /api/usuarios/prueba': PERSONAS, ...rutas };
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (entrada, init) => {
    const clave = `${init?.method ?? 'GET'} ${String(entrada)}`;
    const cuerpo = init?.body ? JSON.parse(String(init.body)) : undefined;
    llamadas.push({ clave, cuerpo });
    if (!(clave in todas)) return respuesta(404, { codigo: 'NO_SIMULADA', mensaje: clave });
    const ruta = todas[clave];
    const valor = typeof ruta === 'function' ? (ruta as (c: unknown) => unknown)(cuerpo) : ruta;
    return valor instanceof Response ? valor : respuesta(200, valor);
  });
  return llamadas;
}

export function renderizarApp(ruta: string, legajo: number | null) {
  guardarLegajoPrueba(legajo);
  return render(
    <MemoryRouter initialEntries={[ruta]} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <ProveedorUsuario>
        <App />
      </ProveedorUsuario>
    </MemoryRouter>,
  );
}
