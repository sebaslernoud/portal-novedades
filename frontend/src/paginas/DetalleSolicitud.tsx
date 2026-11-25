import { ArrowLeft } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';
import { obtenerNovedadesPrevistas, obtenerSolicitud } from '../api/solicitudes';
import type { FilaGms, Renglon, Solicitud } from '../api/tipos';
import PanelDecision from '../componentes/PanelDecision';
import { EstadoSolicitud, IconoTipo, ListaAdvertencias, Mensaje, TablaNovedades } from '../componentes/Varios';
import { useUsuario } from '../contexto/Usuario';
import { ESTADOS, TIPOS, TIPOS_LICENCIA, formatearFecha, formatearFechaHora } from '../textos';

const ETIQUETAS: Record<string, string> = {
  tipo_movimiento: 'Tipo',
  fecha: 'Fecha',
  hora: 'Hora',
  horario_laboral_desde: 'Horario laboral desde',
  horario_laboral_hasta: 'Horario laboral hasta',
  motivo: 'Motivo',
  devoluciones: 'Devolución de horas',
  tipo_licencia: 'Tipo de licencia',
  fecha_desde: 'Fecha desde',
  fecha_hasta: 'Fecha hasta',
  fecha_reintegro: 'Fecha de reincorporación',
  detalle: 'Detalle',
  franco_a_determinar: 'Franco a determinar',
  fecha_franco: 'Fecha del franco',
  hora_desde_franco: 'Inicio del horario laboral',
  hora_hasta_franco: 'Fin del horario laboral',
  dias_trabajados: 'Días con tareas adicionales',
  fecha_cambio: 'Fecha del cambio',
  fecha_devolucion: 'Fecha de devolución',
};

const ACCIONES: Record<string, string> = {
  crear: 'Creó el borrador',
  enviar: 'Envió la solicitud',
  aceptar: 'Aceptó el cambio de turno',
  aprobar: 'Aprobó la solicitud',
  rechazar: 'Rechazó la solicitud',
  sembrar: 'Aprobada (dato de prueba)',
  exportar: 'Exportó a GMS',
  // Lo que ven quienes no son RR.HH. en lugar de "exportar".
  cargar: 'Se cargó la novedad',
};

function valorLegible(clave: string, valor: unknown): string {
  if (typeof valor === 'boolean') return valor ? 'Sí' : 'No';
  if (Array.isArray(valor)) {
    return (valor as Renglon[])
      .map((r) => `${formatearFecha(r.fecha)} de ${r.hora_desde} a ${r.hora_hasta}`)
      .join(' · ');
  }
  if (typeof valor !== 'string') return valor === null || valor === undefined ? '' : String(valor);
  if (clave === 'tipo_movimiento') return valor === 'ingreso' ? 'Ingreso posterior' : 'Retiro anticipado';
  if (clave === 'tipo_licencia') return TIPOS_LICENCIA.find((t) => t.valor === valor)?.nombre ?? valor;
  return /^\d{4}-\d{2}-\d{2}$/.test(valor) ? formatearFecha(valor) : valor;
}

export default function DetalleSolicitud() {
  const { id } = useParams();
  const { state } = useLocation() as { state: { recienEnviada?: boolean } | null };
  const { usuario } = useUsuario();
  const [solicitud, setSolicitud] = useState<Solicitud | null>(null);
  const [novedades, setNovedades] = useState<FilaGms[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    obtenerSolicitud(Number(id))
      .then(setSolicitud)
      .catch((e: Error) => setError(e.message));
  }, [id]);

  // El jefe asignado y RR.HH. ven qué novedades va a generar la solicitud.
  const esAprobador =
    !!usuario &&
    !!solicitud &&
    solicitud.estado !== 'BORRADOR' &&
    (usuario.roles.includes('rrhh') || solicitud.jefe_legajo === usuario.legajo);
  useEffect(() => {
    if (!esAprobador) return;
    obtenerNovedadesPrevistas(Number(id))
      .then(setNovedades)
      .catch(() => setNovedades(null));
  }, [esAprobador, id]);

  if (error) return <Mensaje tipo="error">{error}</Mensaje>;
  if (!solicitud) return <p className="cargando">Cargando…</p>;

  const datos = Object.entries(solicitud.datos).filter(
    ([clave, valor]) => clave !== 'companero_legajo' && valor !== '' && valor !== null && !(Array.isArray(valor) && !valor.length),
  );

  return (
    <section>
      <Link to="/" className="volver">
        <ArrowLeft aria-hidden="true" size={16} />
        Mis solicitudes
      </Link>
      {state?.recienEnviada && <Mensaje tipo="exito">¡Listo! La solicitud se envió.</Mensaje>}
      <div className="encabezado-seccion">
        <div className="encabezado-tipo">
          <IconoTipo tipo={solicitud.tipo} tamano="grande" />
          <h1>{TIPOS[solicitud.tipo].nombre}</h1>
        </div>
        <EstadoSolicitud estado={solicitud.estado} />
      </div>
      <dl className="datos tarjeta">
        <dt>Solicitante</dt>
        <dd>
          {solicitud.solicitante.nombre} ({solicitud.solicitante.legajo})
        </dd>
        {solicitud.companero && (
          <>
            <dt>Compañero</dt>
            <dd>
              {solicitud.companero.nombre} ({solicitud.companero.legajo})
            </dd>
          </>
        )}
        {solicitud.jefe && (
          <>
            <dt>Jefe que aprueba</dt>
            <dd>{solicitud.jefe.nombre ?? solicitud.jefe.legajo}</dd>
          </>
        )}
        {datos.map(([clave, valor]) => (
          <div key={clave} className="dato">
            <dt>{ETIQUETAS[clave] ?? clave}</dt>
            <dd>{valorLegible(clave, valor)}</dd>
          </div>
        ))}
        {solicitud.comentario && (
          <>
            <dt>Comentario</dt>
            <dd>{solicitud.comentario}</dd>
          </>
        )}
      </dl>
      {solicitud.estado !== 'BORRADOR' && <ListaAdvertencias advertencias={solicitud.advertencias} />}
      {novedades && novedades.length > 0 && <TablaNovedades filas={novedades} />}
      {(solicitud.acciones_disponibles ?? []).length > 0 && <PanelDecision solicitud={solicitud} />}
      <h2>Historial</h2>
      <ol className="historial">
        {(solicitud.auditoria ?? []).map((r, i) => (
          <li key={i} className={`historial-${r.estado_nuevo.toLowerCase()}`}>
            <strong>{ACCIONES[r.accion] ?? r.accion}</strong>
            <span className="historial-detalle">
              {r.usuario.nombre} · {formatearFechaHora(r.creado_en)} · {ESTADOS[r.estado_nuevo]}
            </span>
            {r.motivo && <div className="motivo">Motivo: {r.motivo}</div>}
          </li>
        ))}
      </ol>
    </section>
  );
}
