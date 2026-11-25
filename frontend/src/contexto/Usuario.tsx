// Usuario de prueba elegido en pantalla. Se reemplaza por la sesión real cuando haya login.
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { guardarLegajoPrueba, leerLegajoPrueba } from '../api/cliente';
import type { Usuario } from '../api/tipos';
import { listarUsuariosDePrueba } from '../api/usuarios';

type ContextoUsuario = {
  usuario: Usuario | null;
  personas: Usuario[];
  cargando: boolean;
  error: string | null;
  elegir: (legajo: number | null) => void;
};

const Contexto = createContext<ContextoUsuario | null>(null);

export function ProveedorUsuario({ children }: { children: ReactNode }) {
  const [personas, setPersonas] = useState<Usuario[]>([]);
  const [legajo, setLegajo] = useState<number | null>(leerLegajoPrueba);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listarUsuariosDePrueba()
      .then(setPersonas)
      .catch((e: Error) => setError(e.message))
      .finally(() => setCargando(false));
  }, []);

  const elegir = useCallback((nuevo: number | null) => {
    guardarLegajoPrueba(nuevo);
    setLegajo(nuevo);
  }, []);

  const valor = useMemo(
    () => ({ usuario: personas.find((p) => p.legajo === legajo) ?? null, personas, cargando, error, elegir }),
    [personas, legajo, cargando, error, elegir],
  );
  return <Contexto.Provider value={valor}>{children}</Contexto.Provider>;
}

export function useUsuario(): ContextoUsuario {
  const contexto = useContext(Contexto);
  if (!contexto) throw new Error('useUsuario tiene que usarse dentro de ProveedorUsuario');
  return contexto;
}
