import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listarSolicitudes } from '../api/solicitudes';
import type { ListaSolicitudes, Solicitud } from '../api/tipos';
import { EstadoSolicitud } from '../componentes/Varios';
import { TIPOS, formatearFecha } from '../textos';

function Lista({ solicitudes, conSolicitante }: { solicitudes: Solicitud[]; conSolicitante?: boolean }) {
  return (
    <ul className="lista-solicitudes">
      {solicitudes.map((s) => (
        <li key={s.id}>
          <Link to={s.estado === 'BORRADOR' ? `/solicitudes/${s.id}/editar` : `/solicitudes/${s.id}`}>
            <strong>{TIPOS[s.tipo].nombre}</strong>
            <span className="detalle-lista">
              {conSolicitante ? `${s.solicitante.nombre} · ` : ''}
              {s.enviada_en ? `Enviada el ${formatearFecha(s.enviada_en)}` : `Creada el ${formatearFecha(s.creada_en)}`}
              {s.advertencias.length > 0 && ` · ${s.advertencias.length} advertencia(s)`}
            </span>
          </Link>
          <EstadoSolicitud estado={s.estado} />
        </li>
      ))}
    </ul>
  );
}

export default function MisSolicitudes() {
  const [lista, setLista] = useState<ListaSolicitudes | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listarSolicitudes()
      .then(setLista)
      .catch((e: Error) => setError(e.message));
  }, []);

  return (
    <section>
      <div className="encabezado-seccion">
        <h1>Mis solicitudes</h1>
        <Link className="boton" to="/nueva">
          Nueva solicitud
        </Link>
      </div>
      {error && <p className="error">{error}</p>}
      {!lista && !error && <p>Cargando…</p>}
      {lista && lista.mias.length === 0 && <p>Todavía no hiciste ninguna solicitud.</p>}
      {lista && <Lista solicitudes={lista.mias} />}
      {lista && lista.donde_participo.length > 0 && (
        <>
          <h2>Donde participo</h2>
          <p className="subtitulo">Solicitudes de otros donde sos el compañero o el jefe que aprueba.</p>
          <Lista solicitudes={lista.donde_participo} conSolicitante />
        </>
      )}
    </section>
  );
}
