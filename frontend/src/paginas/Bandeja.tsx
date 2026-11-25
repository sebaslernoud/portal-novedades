// Pendientes de aprobación: lo que el usuario tiene para resolver como compañero, jefe o RR.HH.
import { ArrowLeftRight, CircleCheck, Inbox, ShieldCheck, UserRoundCheck } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { obtenerBandeja } from '../api/solicitudes';
import type { Bandeja as DatosBandeja } from '../api/tipos';
import ListaSolicitudes from '../componentes/ListaSolicitudes';
import { Mensaje } from '../componentes/Varios';

const SECCIONES = [
  {
    clave: 'companero',
    titulo: 'Cambios de turno para aceptar',
    ayuda: 'Un compañero te pidió cubrirle un turno.',
    Icono: ArrowLeftRight,
  },
  {
    clave: 'jefe',
    titulo: 'Para aprobar como jefe',
    ayuda: 'Solicitudes de tu equipo que te eligieron como aprobador.',
    Icono: UserRoundCheck,
  },
  {
    clave: 'rrhh',
    titulo: 'Para aprobar como RR.HH.',
    ayuda: 'Ya aprobadas por el jefe. Al aprobarlas quedan listas para cargar en GMS.',
    Icono: ShieldCheck,
  },
] as const;

export default function Bandeja() {
  const { state } = useLocation() as { state: { decision?: string } | null };
  const [bandeja, setBandeja] = useState<DatosBandeja | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    obtenerBandeja()
      .then(setBandeja)
      .catch((e: Error) => setError(e.message));
  }, []);

  const secciones = bandeja ? SECCIONES.filter((s) => bandeja[s.clave].length > 0) : [];
  return (
    <section>
      <h1>Pendientes de aprobación</h1>
      {state?.decision && <Mensaje tipo="exito">{state.decision}</Mensaje>}
      {error && <Mensaje tipo="error">{error}</Mensaje>}
      {!bandeja && !error && <p className="cargando">Cargando…</p>}
      {bandeja && secciones.length === 0 && (
        <div className="vacio">
          <CircleCheck aria-hidden="true" size={40} />
          <p>No tenés nada pendiente de aprobar.</p>
        </div>
      )}
      {bandeja &&
        secciones.map(({ clave, titulo, ayuda, Icono }) => (
          <div key={clave} className="seccion-bandeja">
            <h2>
              <Icono aria-hidden="true" size={20} />
              {titulo}
              <span className="contador">{bandeja[clave].length}</span>
            </h2>
            <p className="subtitulo">{ayuda}</p>
            <ListaSolicitudes solicitudes={bandeja[clave]} conSolicitante />
          </div>
        ))}
      {bandeja && secciones.length > 0 && (
        <p className="nota nota-icono">
          <Inbox aria-hidden="true" size={16} /> Abrí cada solicitud para ver el detalle y decidir.
        </p>
      )}
    </section>
  );
}
