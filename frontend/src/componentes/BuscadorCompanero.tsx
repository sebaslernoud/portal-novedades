// Buscador de empleados por legajo o nombre, para elegir al compañero del cambio de turno.
import { useEffect, useId, useState } from 'react';
import type { Persona } from '../api/tipos';
import { buscarEmpleados } from '../api/usuarios';

type Props = {
  seleccionado: Persona | null;
  error?: string;
  alElegir: (persona: Persona | null) => void;
};

export default function BuscadorCompanero({ seleccionado, error, alElegir }: Props) {
  const id = useId();
  const [texto, setTexto] = useState('');
  const [resultados, setResultados] = useState<Persona[]>([]);

  useEffect(() => {
    if (texto.trim().length < 2) {
      setResultados([]);
      return;
    }
    let vigente = true;
    const espera = setTimeout(() => {
      buscarEmpleados(texto)
        .then((personas) => vigente && setResultados(personas))
        .catch(() => vigente && setResultados([]));
    }, 250);
    return () => {
      vigente = false;
      clearTimeout(espera);
    };
  }, [texto]);

  return (
    <div className={`campo${error ? ' campo-con-error' : ''}`}>
      <label htmlFor={id}>
        Compañero que toma el turno<span aria-hidden="true"> *</span>
      </label>
      {seleccionado ? (
        <div className="seleccionado">
          <span>
            {seleccionado.nombre} ({seleccionado.legajo})
          </span>
          <button type="button" className="boton-secundario" onClick={() => alElegir(null)}>
            Cambiar
          </button>
        </div>
      ) : (
        <>
          <input
            id={id}
            type="search"
            placeholder="Buscá por legajo o nombre"
            value={texto}
            required
            aria-invalid={error ? true : undefined}
            onChange={(e) => setTexto(e.target.value)}
          />
          {resultados.length > 0 && (
            <ul className="resultados" aria-label="Resultados de la búsqueda">
              {resultados.map((p) => (
                <li key={p.legajo}>
                  <button type="button" onClick={() => alElegir(p)}>
                    {p.nombre} ({p.legajo})
                  </button>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
      {error && (
        <small className="error" role="alert">
          {error}
        </small>
      )}
    </div>
  );
}
