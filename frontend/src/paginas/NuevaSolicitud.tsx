// Elegir formulario → completar → revisar advertencias y novedades → guardar borrador o enviar.
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ErrorApi } from '../api/cliente';
import { crearBorrador, editarBorrador, enviarSolicitud, obtenerSolicitud, previsualizar } from '../api/solicitudes';
import type { CuerpoSolicitud, DatosPorTipo, Errores, Previsualizacion, TipoSolicitud } from '../api/tipos';
import { CampoTexto } from '../componentes/Campos';
import SelectorJefe from '../componentes/SelectorJefe';
import { ListaAdvertencias, TablaNovedades } from '../componentes/Varios';
import { FormularioDeTipo } from '../formularios';
import { TIPOS, datosIniciales } from '../textos';

type Datos = DatosPorTipo[TipoSolicitud];

export default function NuevaSolicitud() {
  const { id } = useParams();
  const navegar = useNavigate();
  const [borradorId, setBorradorId] = useState<number | null>(id ? Number(id) : null);
  const [tipo, setTipo] = useState<TipoSolicitud | null>(null);
  const [datos, setDatos] = useState<Datos | null>(null);
  const [jefe, setJefe] = useState<number | null>(null);
  const [comentario, setComentario] = useState('');
  const [errores, setErrores] = useState<Errores>({});
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [revision, setRevision] = useState<Previsualizacion | null>(null);
  const [ocupado, setOcupado] = useState(false);

  useEffect(() => {
    if (!id) return;
    obtenerSolicitud(Number(id))
      .then((s) => {
        if (s.estado !== 'BORRADOR') {
          navegar(`/solicitudes/${s.id}`, { replace: true });
          return;
        }
        setTipo(s.tipo);
        setDatos({ ...datosIniciales(s.tipo), ...s.datos } as Datos);
        setJefe(s.jefe_legajo);
        setComentario(s.comentario ?? '');
      })
      .catch((e: Error) => setMensaje(e.message));
  }, [id, navegar]);

  const elegirTipo = (nuevo: TipoSolicitud) => {
    setTipo(nuevo);
    setDatos(datosIniciales(nuevo));
    setErrores({});
    setMensaje(null);
  };

  const cambiarDatos = (parcial: Partial<Datos>) => {
    setDatos((actuales) => (actuales ? ({ ...actuales, ...parcial } as Datos) : actuales));
    setRevision(null);
  };

  const ejecutar = async (accion: () => Promise<void>) => {
    setOcupado(true);
    setMensaje(null);
    try {
      await accion();
    } catch (e) {
      if (e instanceof ErrorApi) {
        setErrores(e.porCampo());
        setMensaje(e.message);
      } else {
        setMensaje('No se pudo conectar con el servidor. Probá de nuevo.');
      }
    } finally {
      setOcupado(false);
    }
  };

  if (!tipo || !datos) {
    return (
      <section>
        <h1>Nueva solicitud</h1>
        {mensaje && <p className="error">{mensaje}</p>}
        <p>¿Qué querés pedir?</p>
        <div className="grilla-tipos">
          {(Object.keys(TIPOS) as TipoSolicitud[]).map((t) => (
            <button key={t} type="button" className="tarjeta-tipo" onClick={() => elegirTipo(t)}>
              <strong>{TIPOS[t].nombre}</strong>
              <span>{TIPOS[t].descripcion}</span>
            </button>
          ))}
        </div>
      </section>
    );
  }

  const cuerpo: CuerpoSolicitud = { tipo, jefe_legajo: jefe, comentario, datos };
  const guardar = async () => {
    const guardada = borradorId ? await editarBorrador(borradorId, cuerpo) : await crearBorrador(cuerpo);
    setBorradorId(guardada.id);
    return guardada.id;
  };
  const companero = tipo === 'cambio_turno' ? (datos as DatosPorTipo['cambio_turno']).companero_legajo : null;

  if (revision) {
    return (
      <section>
        <h1>Revisá tu solicitud</h1>
        <p className="subtitulo">{TIPOS[tipo].nombre}</p>
        {mensaje && <p className="error">{mensaje}</p>}
        <ListaAdvertencias advertencias={revision.advertencias} />
        <TablaNovedades filas={revision.novedades} />
        <div className="acciones">
          <button type="button" className="boton-secundario" onClick={() => setRevision(null)} disabled={ocupado}>
            Volver a editar
          </button>
          <button
            type="button"
            disabled={ocupado}
            onClick={() =>
              ejecutar(async () => {
                const enviada = await enviarSolicitud(await guardar());
                navegar(`/solicitudes/${enviada.id}`, { state: { recienEnviada: true } });
              })
            }
          >
            Enviar solicitud
          </button>
        </div>
      </section>
    );
  }

  return (
    <section>
      <h1>{TIPOS[tipo].nombre}</h1>
      {!borradorId && (
        <button type="button" className="enlace" onClick={() => setTipo(null)}>
          Elegir otro formulario
        </button>
      )}
      <form
        noValidate
        className="formulario"
        onSubmit={(e) => {
          e.preventDefault();
          ejecutar(async () => {
            setRevision(await previsualizar(cuerpo));
            setErrores({});
          });
        }}
      >
        <FormularioDeTipo tipo={tipo} datos={datos} errores={errores} cambiar={cambiarDatos} />
        <SelectorJefe
          valor={jefe}
          excluir={companero}
          error={errores['jefe_legajo']}
          alCambiar={(legajo) => {
            setJefe(legajo);
            setRevision(null);
          }}
        />
        <CampoTexto
          etiqueta="Comentario para los aprobadores"
          multilinea
          ayuda="No se carga en GMS."
          valor={comentario}
          error={errores['comentario']}
          alCambiar={setComentario}
        />
        {mensaje && (
          <p className={Object.keys(errores).length ? 'error' : 'aviso'} role="status">
            {mensaje}
          </p>
        )}
        <div className="acciones">
          <button
            type="button"
            className="boton-secundario"
            disabled={ocupado}
            onClick={() =>
              ejecutar(async () => {
                await guardar();
                setErrores({});
                setMensaje('Borrador guardado.');
              })
            }
          >
            Guardar borrador
          </button>
          <button type="submit" disabled={ocupado}>
            Revisar
          </button>
        </div>
      </form>
    </section>
  );
}
