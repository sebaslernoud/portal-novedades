// Lista de 0 a 4 renglones (fecha, hora desde, hora hasta): devoluciones o días trabajados.
import { Plus, Trash2 } from 'lucide-react';
import type { Errores, Renglon } from '../api/tipos';
import { CampoFecha, CampoHora, ErrorCampo } from './Campos';

const MAXIMO = 4;

type Props = {
  titulo: string;
  campo: string;
  renglones: Renglon[];
  errores: Errores;
  alCambiar: (renglones: Renglon[]) => void;
};

export default function Renglones({ titulo, campo, renglones, errores, alCambiar }: Props) {
  const cambiar = (indice: number, parcial: Partial<Renglon>) =>
    alCambiar(renglones.map((r, i) => (i === indice ? { ...r, ...parcial } : r)));

  return (
    <fieldset className="renglones">
      <legend>{titulo}</legend>
      {errores[`datos.${campo}`] && <ErrorCampo>{errores[`datos.${campo}`]}</ErrorCampo>}
      {renglones.map((renglon, i) => {
        const error = (dato: keyof Renglon) => errores[`datos.${campo}.${i}.${dato}`];
        return (
          <div className="renglon" key={i}>
            <span className="renglon-numero" aria-hidden="true">
              {i + 1}
            </span>
            <div className="renglon-campos">
              <CampoFecha
                etiqueta={`Fecha ${i + 1}`}
                obligatorio
                valor={renglon.fecha}
                error={error('fecha')}
                alCambiar={(fecha) => cambiar(i, { fecha })}
              />
              <CampoHora
                etiqueta="Desde"
                obligatorio
                valor={renglon.hora_desde}
                error={error('hora_desde')}
                alCambiar={(hora_desde) => cambiar(i, { hora_desde })}
              />
              <CampoHora
                etiqueta="Hasta"
                obligatorio
                valor={renglon.hora_hasta}
                error={error('hora_hasta')}
                alCambiar={(hora_hasta) => cambiar(i, { hora_hasta })}
              />
            </div>
            <button
              type="button"
              className="boton-quitar"
              onClick={() => alCambiar(renglones.filter((_, j) => j !== i))}
            >
              <Trash2 aria-hidden="true" size={16} />
              Quitar
            </button>
          </div>
        );
      })}
      {renglones.length < MAXIMO && (
        <button
          type="button"
          className="boton-agregar"
          onClick={() => alCambiar([...renglones, { fecha: '', hora_desde: '', hora_hasta: '' }])}
        >
          <Plus aria-hidden="true" size={18} />
          Agregar renglón
        </button>
      )}
    </fieldset>
  );
}
