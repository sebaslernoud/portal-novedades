import { ChevronRight, FilePlus2, Inbox, TriangleAlert } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listarSolicitudes } from '../api/solicitudes';
import type { ListaSolicitudes, Solicitud } from '../api/tipos';
import { EstadoSolicitud, IconoTipo, Mensaje } from '../componentes/Varios';
import { useUsuario } from '../contexto/Usuario';
import { TIPOS, formatearFecha } from '../textos';

function Lista({ solicitudes, conSolicitante }: { solicitudes: Solicitud[]; conSolicitante?: boolean }) {
  return (
    <ul className="lista-solicitudes">
      {solicitudes.map((s) => (
        <li key={s.id}>
          <Link
            className="item-solicitud"
            to={s.estado === 'BORRADOR' ? `/solicitudes/${s.id}/editar` : `/solicitudes/${s.id}`}
          >
            <IconoTipo tipo={s.tipo} />
            <span className="item-texto">
              <strong>{TIPOS[s.tipo].nombre}</strong>
              <span className="detalle-lista">
                {conSolicitante ? `${s.solicitante.nombre} · ` : ''}
                {s.enviada_en ? `Enviada el ${formatearFecha(s.enviada_en)}` : `Creada el ${formatearFecha(s.creada_en)}`}
                {s.advertencias.length > 0 && (
                  <span className="contador-advertencias">
                    <TriangleAlert aria-hidden="true" size={14} />
                    {` ${s.advertencias.length} advertencia(s)`}
                  </span>
                )}
              </span>
            </span>
            <EstadoSolicitud estado={s.estado} />
            <ChevronRight aria-hidden="true" size={18} className="item-flecha" />
          </Link>
        </li>
      ))}
    </ul>
  );
}

export default function MisSolicitudes() {
  const { usuario } = useUsuario();
  const [lista, setLista] = useState<ListaSolicitudes | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listarSolicitudes()
      .then(setLista)
      .catch((e: Error) => setError(e.message));
  }, []);

  const nombre = usuario?.nombre.split(' ')[0] ?? '';
  return (
    <section>
      <div className="encabezado-seccion">
        <div>
          <p className="saludo">Hola, {nombre.charAt(0) + nombre.slice(1).toLowerCase()}</p>
          <h1>Mis solicitudes</h1>
        </div>
        <Link className="boton" to="/nueva">
          <FilePlus2 aria-hidden="true" size={18} />
          Nueva solicitud
        </Link>
      </div>
      {error && <Mensaje tipo="error">{error}</Mensaje>}
      {!lista && !error && <p className="cargando">Cargando…</p>}
      {lista && lista.mias.length === 0 && (
        <div className="vacio">
          <Inbox aria-hidden="true" size={40} />
          <p>Todavía no hiciste ninguna solicitud.</p>
          <Link to="/nueva">Crear la primera</Link>
        </div>
      )}
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
