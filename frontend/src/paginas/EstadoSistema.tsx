import { Activity } from 'lucide-react';
import { useEffect, useState } from 'react';
import { obtenerSalud, type EstadoSalud } from '../api/cliente';

export default function EstadoSistema() {
  const [salud, setSalud] = useState<EstadoSalud | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    obtenerSalud().then(setSalud).catch((e: Error) => setError(e.message));
  }, []);

  const ok = salud?.estado === 'ok';
  return (
    <section className="tarjeta estado-sistema" aria-live="polite">
      <h2>
        <Activity aria-hidden="true" size={20} /> Estado del sistema
      </h2>
      {error && <p className="texto-error">No se pudo conectar con el backend: {error}</p>}
      {!error && !salud && <p>Consultando…</p>}
      {salud && (
        <ul>
          <li>
            <span className={`punto ${ok ? 'punto-ok' : 'punto-error'}`} aria-hidden="true" />
            Backend: {ok ? 'funcionando' : 'con problemas'}
          </li>
          <li>Base de datos: {salud.base_de_datos}</li>
          {salud.migracion && <li>Migración: {salud.migracion}</li>}
        </ul>
      )}
    </section>
  );
}
