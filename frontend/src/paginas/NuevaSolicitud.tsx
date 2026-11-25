// Elegir formulario → completar → revisar advertencias y novedades → guardar borrador o enviar.
import { ArrowLeft, Eye, LoaderCircle, Save, Send } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ErrorApi } from '../api/cliente';
import { crearBorrador, editarBorrador, enviarSolicitud, obtenerSolicitud, previsualizar } from '../api/solicitudes';
import type { CuerpoSolicitud, DatosPorTipo, Errores, Previsualizacion, TipoSolicitud } from '../api/tipos';
import { CampoTexto } from '../componentes/Campos';
import SelectorJefe from '../componentes/SelectorJefe';
import { IconoTipo, ListaAdvertencias, Mensaje, TablaNovedades } from '../componentes/Varios';
import { FormularioDeTipo } from '../formularios';
import { TIPOS, datosIniciales } from '../textos';

type Datos = DatosPorTipo[TipoSolicitud];
type Aviso = { tipo: 'error' | 'exito'; texto: string };

// Mientras una acción está en curso, el ícono del botón pasa a ser un spinner.
const IconoAccion = ({ ocupado, Icono }: { ocupado: boolean; Icono: typeof Send }) =>
  ocupado ? (
    <LoaderCircle aria-hidden="true" size={18} className="girando" />
  ) : (
    <Icono aria-hidden="true" size={18} />
  );

function EncabezadoTipo({ tipo, titulo }: { tipo: TipoSolicitud; titulo?: string }) {
  return (
    <div className="encabezado-tipo">
      <IconoTipo tipo={tipo} tamano="grande" />
      <div>
        {titulo && <p className="subtitulo">{TIPOS[tipo].nombre}</p>}
        <h1>{titulo ?? TIPOS[tipo].nombre}</h1>
      </div>
    </div>
  );
}

export default function NuevaSolicitud() {
  const { id } = useParams();
  const navegar = useNavigate();
  const [borradorId, setBorradorId] = useState<number | null>(id ? Number(id) : null);
  const [tipo, setTipo] = useState<TipoSolicitud | null>(null);
  const [datos, setDatos] = useState<Datos | null>(null);
  const [jefe, setJefe] = useState<number | null>(null);
  const [comentario, setComentario] = useState('');
  const [errores, setErrores] = useState<Errores>({});
  const [aviso, setAviso] = useState<Aviso | null>(null);
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
      .catch((e: Error) => setAviso({ tipo: 'error', texto: e.message }));
  }, [id, navegar]);

  const elegirTipo = (nuevo: TipoSolicitud) => {
    setTipo(nuevo);
    setDatos(datosIniciales(nuevo));
    setErrores({});
    setAviso(null);
  };

  const cambiarDatos = (parcial: Partial<Datos>) => {
    setDatos((actuales) => (actuales ? ({ ...actuales, ...parcial } as Datos) : actuales));
    setRevision(null);
  };

  const ejecutar = async (accion: () => Promise<void>) => {
    setOcupado(true);
    setAviso(null);
    try {
      await accion();
    } catch (e) {
      if (e instanceof ErrorApi) {
        setErrores(e.porCampo());
        setAviso({ tipo: 'error', texto: e.message });
      } else {
        setAviso({ tipo: 'error', texto: 'No se pudo conectar con el servidor. Probá de nuevo.' });
      }
    } finally {
      setOcupado(false);
    }
  };

  const mensaje = aviso && <Mensaje tipo={aviso.tipo}>{aviso.texto}</Mensaje>;

  if (!tipo || !datos) {
    return (
      <section>
        <h1>Nueva solicitud</h1>
        {mensaje}
        <p className="subtitulo">¿Qué querés pedir?</p>
        <div className="grilla-tipos">
          {(Object.keys(TIPOS) as TipoSolicitud[]).map((t) => {
            const { nombre, descripcion, icono: Icono, color } = TIPOS[t];
            return (
              <button key={t} type="button" className={`tarjeta-tipo fondo-${color}`} onClick={() => elegirTipo(t)}>
                <span className="tarjeta-tipo-icono" aria-hidden="true">
                  <Icono size={28} />
                </span>
                <strong>{nombre}</strong>
                <span>{descripcion}</span>
              </button>
            );
          })}
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
        <EncabezadoTipo tipo={tipo} titulo="Revisá tu solicitud" />
        {mensaje}
        <div className="tarjeta">
          <ListaAdvertencias advertencias={revision.advertencias} />
          <TablaNovedades filas={revision.novedades} />
          <div className="acciones">
            <button type="button" className="boton-secundario" onClick={() => setRevision(null)} disabled={ocupado}>
              <ArrowLeft aria-hidden="true" size={18} />
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
              <IconoAccion ocupado={ocupado} Icono={Send} />
              Enviar solicitud
            </button>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section>
      <EncabezadoTipo tipo={tipo} />
      {!borradorId && (
        <button type="button" className="enlace" onClick={() => setTipo(null)}>
          <ArrowLeft aria-hidden="true" size={16} />
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
        <div className="separador" />
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
        {mensaje}
        <div className="acciones">
          <button
            type="button"
            className="boton-secundario"
            disabled={ocupado}
            onClick={() =>
              ejecutar(async () => {
                await guardar();
                setErrores({});
                setAviso({ tipo: 'exito', texto: 'Borrador guardado.' });
              })
            }
          >
            <Save aria-hidden="true" size={18} />
            Guardar borrador
          </button>
          <button type="submit" disabled={ocupado}>
            <IconoAccion ocupado={ocupado} Icono={Eye} />
            Revisar
          </button>
        </div>
      </form>
    </section>
  );
}
