import { useEffect, useState } from 'react';
import { obtenerSalud, type EstadoSalud } from './api/cliente';

export default function App() {
  const [salud, setSalud] = useState<EstadoSalud | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    obtenerSalud().then(setSalud).catch((e: Error) => setError(e.message));
  }, []);

  return (
    <main className="contenedor">
      <h1>Portal de Novedades</h1>
      <p>Solicitudes de licencias, francos y cambios de turno.</p>
      <section className="tarjeta" aria-live="polite">
        <h2>Estado del sistema</h2>
        {error && <p className="error">No se pudo conectar con el backend: {error}</p>}
        {!error && !salud && <p>Consultando…</p>}
        {salud && (
          <ul>
            <li>Backend: {salud.estado === 'ok' ? 'funcionando' : 'con problemas'}</li>
            <li>Base de datos: {salud.base_de_datos}</li>
            {salud.migracion && <li>Migración: {salud.migracion}</li>}
          </ul>
        )}
      </section>
    </main>
  );
}
