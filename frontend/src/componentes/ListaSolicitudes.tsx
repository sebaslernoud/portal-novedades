import { ChevronRight, TriangleAlert } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { Solicitud } from '../api/tipos';
import { TIPOS, formatearFecha } from '../textos';
import { EstadoSolicitud, IconoTipo } from './Varios';

type Props = { solicitudes: Solicitud[]; conSolicitante?: boolean };

// Tarjetas de solicitudes: un borrador abre el formulario; el resto, el detalle.
export default function ListaSolicitudes({ solicitudes, conSolicitante }: Props) {
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
