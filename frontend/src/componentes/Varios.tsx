// Piezas chicas de presentación: advertencias, estado y tabla de novedades GMS.
import type { EstadoSolicitud as Estado, FilaGms } from '../api/tipos';
import { ESTADOS, formatearFecha } from '../textos';

export function ListaAdvertencias({ advertencias }: { advertencias: string[] }) {
  if (advertencias.length === 0) {
    return <p className="sin-advertencias">Sin advertencias.</p>;
  }
  return (
    <section className="advertencias" aria-label="Advertencias">
      <h3>Advertencias para los aprobadores</h3>
      <p>No impiden enviar la solicitud: tu jefe y RR.HH. las van a ver.</p>
      <ul>
        {advertencias.map((a) => (
          <li key={a}>{a}</li>
        ))}
      </ul>
    </section>
  );
}

export function EstadoSolicitud({ estado }: { estado: Estado }) {
  return <span className={`estado estado-${estado.toLowerCase()}`}>{ESTADOS[estado]}</span>;
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
              <td>{f.concepto}</td>
              <td>{f.cantidad}</td>
              <td>{formatearFecha(f.fecha_desde)}</td>
              <td>{formatearFecha(f.fecha_hasta)}</td>
              <td>{f.hora_desde ? `${f.hora_desde}–${f.hora_hasta ?? ''}` : ''}</td>
              <td>{f.observaciones}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
