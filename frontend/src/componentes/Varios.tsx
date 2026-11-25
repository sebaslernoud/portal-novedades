// Piezas de presentación compartidas: mensajes, advertencias, estado, ícono de tipo y tabla de novedades.
import {
  Ban,
  CircleAlert,
  CircleCheck,
  CircleX,
  FileCheck2,
  FilePen,
  Hourglass,
  Info,
  TriangleAlert,
  type LucideIcon,
} from 'lucide-react';
import type { ReactNode } from 'react';
import type { EstadoSolicitud as Estado, FilaGms, TipoSolicitud } from '../api/tipos';
import { ESTADOS, TIPOS, formatearFecha } from '../textos';

type TipoMensaje = 'error' | 'info' | 'exito';

const ICONO_MENSAJE: Record<TipoMensaje, LucideIcon> = { error: CircleAlert, info: Info, exito: CircleCheck };

// Error en rojo (alertas), información en celeste y éxito en turquesa.
export function Mensaje({ tipo, children }: { tipo: TipoMensaje; children: ReactNode }) {
  const Icono = ICONO_MENSAJE[tipo];
  return (
    <div className={`mensaje mensaje-${tipo}`} role={tipo === 'error' ? 'alert' : 'status'}>
      <Icono className="mensaje-icono" aria-hidden="true" size={20} />
      <div className="mensaje-contenido">{children}</div>
    </div>
  );
}

export function IconoTipo({ tipo, tamano = 'normal' }: { tipo: TipoSolicitud; tamano?: 'normal' | 'grande' }) {
  const { icono: Icono, color } = TIPOS[tipo];
  return (
    <span className={`icono-tipo icono-tipo-${tamano} fondo-${color}`} aria-hidden="true">
      <Icono size={tamano === 'grande' ? 28 : 20} />
    </span>
  );
}

export function ListaAdvertencias({ advertencias }: { advertencias: string[] }) {
  if (advertencias.length === 0) {
    return (
      <p className="sin-advertencias">
        <CircleCheck aria-hidden="true" size={18} /> Sin advertencias.
      </p>
    );
  }
  return (
    <section className="advertencias" aria-label="Advertencias">
      <h3>
        <TriangleAlert aria-hidden="true" size={20} /> Advertencias para los aprobadores
      </h3>
      <p>No impiden enviar la solicitud: tu jefe y RR.HH. las van a ver.</p>
      <ul>
        {advertencias.map((a) => (
          <li key={a}>{a}</li>
        ))}
      </ul>
    </section>
  );
}

const ICONO_ESTADO: Record<Estado, LucideIcon> = {
  BORRADOR: FilePen,
  PENDIENTE_COMPANERO: Hourglass,
  PENDIENTE_JEFE: Hourglass,
  PENDIENTE_RRHH: Hourglass,
  APROBADA: CircleCheck,
  EXPORTADA: FileCheck2,
  CARGADA_GMS: FileCheck2,
  ERROR_CARGA: CircleAlert,
  RECHAZADA: CircleX,
  CANCELADA: Ban,
};

export function EstadoSolicitud({ estado }: { estado: Estado }) {
  const Icono = ICONO_ESTADO[estado];
  return (
    <span className={`estado estado-${estado.toLowerCase()}`}>
      <Icono aria-hidden="true" size={14} />
      {ESTADOS[estado]}
    </span>
  );
}

export function TablaNovedades({ filas }: { filas: FilaGms[] }) {
  return (
    <div className="tabla-desplazable">
      <table>
        <caption>Novedades que se cargan en GMS</caption>
        <thead>
          <tr>
            <th scope="col">Legajo</th>
            <th scope="col">Concepto</th>
            <th scope="col">Cantidad</th>
            <th scope="col">Desde</th>
            <th scope="col">Hasta</th>
            <th scope="col">Horas</th>
            <th scope="col">Observaciones</th>
          </tr>
        </thead>
        <tbody>
          {filas.map((f, i) => (
            <tr key={i}>
              <td>{f.legajo}</td>
              <td>
                <span className="chip">{f.concepto}</span>
              </td>
              <td>{f.cantidad}</td>
              <td>{formatearFecha(f.fecha_desde)}</td>
              <td>{formatearFecha(f.fecha_hasta)}</td>
              <td>{f.hora_desde ? `${f.hora_desde}–${f.hora_hasta ?? ''}` : ''}</td>
              <td className="celda-observaciones">{f.observaciones}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
