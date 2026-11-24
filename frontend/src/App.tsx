import { NavLink, Route, Routes } from 'react-router-dom';
import SelectorUsuarioPrueba from './componentes/SelectorUsuarioPrueba';
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
          <strong className="marca">Portal de Novedades</strong>
          {usuario && (
            <nav aria-label="Principal">
              <NavLink to="/" end>
                Mis solicitudes
              </NavLink>
              <NavLink to="/nueva">Nueva solicitud</NavLink>
              {esRrhh && <NavLink to="/exportacion">Exportación GMS</NavLink>}
            </nav>
          )}
          <SelectorUsuarioPrueba />
        </div>
      </header>
      <main className="contenedor">
        {error && <p className="error">No se pudo cargar la lista de usuarios de prueba: {error}</p>}
        {!usuario ? (
          !cargando && (
            <>
              <h1>Portal de Novedades</h1>
              <p>Solicitudes de licencias, francos y cambios de turno.</p>
              <p className="aviso">Todavía no hay login: elegí un usuario de prueba arriba para empezar.</p>
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
