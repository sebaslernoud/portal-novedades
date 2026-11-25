import { FilePlus2, Inbox } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listarSolicitudes } from '../api/solicitudes';
import type { ListaSolicitudes as Listas } from '../api/tipos';
import ListaSolicitudes from '../componentes/ListaSolicitudes';
import { Mensaje } from '../componentes/Varios';
import { useUsuario } from '../contexto/Usuario';

export default function MisSolicitudes() {
  const { usuario } = useUsuario();
  const [lista, setLista] = useState<Listas | null>(null);
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
      {lista && <ListaSolicitudes solicitudes={lista.mias} />}
      {lista && lista.donde_participo.length > 0 && (
        <>
          <h2>Donde participo</h2>
          <p className="subtitulo">Solicitudes de otros donde sos el compañero o el jefe que aprueba.</p>
          <ListaSolicitudes solicitudes={lista.donde_participo} conSolicitante />
        </>
      )}
    </section>
  );
}
