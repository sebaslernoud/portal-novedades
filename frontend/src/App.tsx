import { ClipboardList, FilePlus2, FileSpreadsheet, HeartPulse } from 'lucide-react';
import { NavLink, Route, Routes } from 'react-router-dom';
import SelectorUsuarioPrueba from './componentes/SelectorUsuarioPrueba';
import { Mensaje } from './componentes/Varios';
import { useUsuario } from './contexto/Usuario';
import DetalleSolicitud from './paginas/DetalleSolicitud';
import EstadoSistema from './paginas/EstadoSistema';
import ExportacionRrhh from './paginas/ExportacionRrhh';
import MisSolicitudes from './paginas/MisSolicitudes';
import NuevaSolicitud from './paginas/NuevaSolicitud';

export default function App() {
  const { usuario, cargando, error } = useUsuario();
  const esRrhh = usuario?.roles.includes('rrhh') ?? false;

  return (
    <>
      <header className="encabezado">
        <div className="contenedor encabezado-interno">
          <span className="marca">
            <HeartPulse aria-hidden="true" size={30} className="marca-icono" />
            <span className="marca-texto">
              Portal de <strong>Novedades</strong>
            </span>
          </span>
          <SelectorUsuarioPrueba />
        </div>
        {usuario && (
          <nav className="menu" aria-label="Principal">
            <div className="contenedor menu-interno">
              <NavLink to="/" end>
                <ClipboardList aria-hidden="true" size={18} />
                Mis solicitudes
              </NavLink>
              <NavLink to="/nueva">
                <FilePlus2 aria-hidden="true" size={18} />
                Nueva solicitud
              </NavLink>
              {esRrhh && (
                <NavLink to="/exportacion">
                  <FileSpreadsheet aria-hidden="true" size={18} />
                  Exportación GMS
                </NavLink>
              )}
            </div>
          </nav>
        )}
      </header>
      <main className="contenedor contenido">
        {error && <Mensaje tipo="error">No se pudo cargar la lista de usuarios de prueba: {error}</Mensaje>}
        {!usuario ? (
          !cargando && (
            <>
              <section className="bienvenida">
                <h1>Tus novedades, sin papeles</h1>
                <p>Pedí licencias, francos, cambios de turno y retiros fuera de horario desde cualquier dispositivo.</p>
                <p className="bienvenida-aviso">
                  Todavía no hay login: elegí un usuario de prueba arriba para empezar.
                </p>
              </section>
              <EstadoSistema />
            </>
          )
        ) : (
          <Routes key={usuario.legajo}>
            <Route path="/" element={<MisSolicitudes />} />
            <Route path="/nueva" element={<NuevaSolicitud />} />
            <Route path="/solicitudes/:id" element={<DetalleSolicitud />} />
            <Route path="/solicitudes/:id/editar" element={<NuevaSolicitud />} />
            <Route path="/exportacion" element={esRrhh ? <ExportacionRrhh /> : <p>Solo para RR.HH.</p>} />
            <Route path="/estado" element={<EstadoSistema />} />
            <Route path="*" element={<p>Esta página no existe.</p>} />
          </Routes>
        )}
      </main>
    </>
  );
}
