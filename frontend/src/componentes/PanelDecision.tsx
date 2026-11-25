// "Tu decisión": aprobar (o aceptar el cambio de turno) o rechazar con motivo.
import { CircleCheck, CircleX, LoaderCircle } from 'lucide-react';
import { useId, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ErrorApi } from '../api/cliente';
import { aprobarSolicitud, rechazarSolicitud } from '../api/solicitudes';
import type { Solicitud } from '../api/tipos';
import { ErrorCampo } from './Campos';
import { Mensaje } from './Varios';

const MOTIVO_MINIMO = 5;

export default function PanelDecision({ solicitud }: { solicitud: Solicitud }) {
  const navegar = useNavigate();
  const idMotivo = useId();
  const [rechazando, setRechazando] = useState(false);
  const [motivo, setMotivo] = useState('');
  const [errorMotivo, setErrorMotivo] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ocupado, setOcupado] = useState(false);

  const esCompanero = solicitud.estado === 'PENDIENTE_COMPANERO';

  const decidir = async (accion: () => Promise<Solicitud>, mensaje: string) => {
    setOcupado(true);
    setError(null);
    try {
      await accion();
      navegar('/bandeja', { state: { decision: mensaje } });
    } catch (e) {
      if (e instanceof ErrorApi && e.porCampo().motivo) setErrorMotivo(e.porCampo().motivo);
      else setError(e instanceof Error ? e.message : 'No se pudo conectar con el servidor.');
      setOcupado(false);
    }
  };

  const confirmarRechazo = () => {
    if (motivo.trim().length < MOTIVO_MINIMO) {
      setErrorMotivo(`Escribí el motivo del rechazo (mínimo ${MOTIVO_MINIMO} caracteres).`);
      return;
    }
    setErrorMotivo(null);
    decidir(() => rechazarSolicitud(solicitud.id, motivo.trim()), 'Rechazaste la solicitud.');
  };

  return (
    <section className="panel-decision" aria-label="Tu decisión">
      <h2>Tu decisión</h2>
      <p className="subtitulo">
        {esCompanero
          ? `${solicitud.solicitante.nombre} te pidió cubrirle un turno. Si aceptás, pasa a su jefe.`
          : 'Revisá los datos y las advertencias antes de decidir. El rechazo es definitivo.'}
      </p>
      {error && <Mensaje tipo="error">{error}</Mensaje>}
      {rechazando ? (
        <div className={`campo${errorMotivo ? ' campo-con-error' : ''}`}>
          <label htmlFor={idMotivo}>
            Motivo del rechazo<span className="obligatorio" aria-hidden="true">{' *'}</span>
          </label>
          <textarea
            id={idMotivo}
            rows={3}
            maxLength={500}
            required
            value={motivo}
            aria-invalid={errorMotivo ? true : undefined}
            onChange={(e) => setMotivo(e.target.value)}
          />
          {errorMotivo && <ErrorCampo>{errorMotivo}</ErrorCampo>}
          <div className="acciones">
            <button type="button" className="boton-secundario" disabled={ocupado} onClick={() => setRechazando(false)}>
              Cancelar
            </button>
            <button type="button" className="boton-peligro" disabled={ocupado} onClick={confirmarRechazo}>
              {ocupado ? <LoaderCircle aria-hidden="true" size={18} className="girando" /> : <CircleX aria-hidden="true" size={18} />}
              Confirmar rechazo
            </button>
          </div>
        </div>
      ) : (
        <div className="acciones">
          <button type="button" className="boton-secundario boton-rechazar" disabled={ocupado} onClick={() => setRechazando(true)}>
            <CircleX aria-hidden="true" size={18} />
            Rechazar
          </button>
          <button
            type="button"
            disabled={ocupado}
            onClick={() =>
              decidir(
                () => aprobarSolicitud(solicitud.id),
                esCompanero ? 'Aceptaste el cambio de turno.' : 'Aprobaste la solicitud.',
              )
            }
          >
            {ocupado ? (
              <LoaderCircle aria-hidden="true" size={18} className="girando" />
            ) : (
              <CircleCheck aria-hidden="true" size={18} />
            )}
            {esCompanero ? 'Aceptar cambio' : 'Aprobar'}
          </button>
        </div>
      )}
    </section>
  );
}
