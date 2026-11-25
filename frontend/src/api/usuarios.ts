import { pedir } from './cliente';
import type { Persona, Usuario } from './tipos';

export const listarUsuariosDePrueba = () => pedir<Usuario[]>('/usuarios/prueba');

export const obtenerUsuarioActual = () => pedir<Usuario>('/usuarios/actual');

export const listarJefes = () => pedir<Persona[]>('/usuarios/jefes');

export const buscarEmpleados = (texto: string) =>
  pedir<Persona[]>(`/usuarios?buscar=${encodeURIComponent(texto)}`);
