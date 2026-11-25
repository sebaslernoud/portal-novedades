import type { Errores } from '../api/tipos';

export type PropsFormulario<T> = {
  datos: T;
  errores: Errores;
  cambiar: (parcial: Partial<T>) => void;
};
