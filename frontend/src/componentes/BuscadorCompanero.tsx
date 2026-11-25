// Buscador de empleados por legajo o nombre, para elegir al compañero del cambio de turno.
import { Search, UserRound } from 'lucide-react';
import { useEffect, useId, useState } from 'react';
import type { Persona } from '../api/tipos';
import { buscarEmpleados } from '../api/usuarios';
import { ErrorCampo, MarcaObligatorio } from './Campos';

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
        Compañero que toma el turno
        <MarcaObligatorio />
      </label>
      {seleccionado ? (
        <div className="seleccionado">
          <UserRound aria-hidden="true" size={20} />
          <span>
            {seleccionado.nombre} ({seleccionado.legajo})
          </span>
          <button type="button" className="boton-secundario boton-chico" onClick={() => alElegir(null)}>
            Cambiar
          </button>
        </div>
      ) : (
        <>
          <div className="entrada-con-icono">
            <Search aria-hidden="true" size={18} />
            <input
              id={id}
              type="search"
              placeholder="Buscá por legajo o nombre"
              value={texto}
              required
              aria-invalid={error ? true : undefined}
              onChange={(e) => setTexto(e.target.value)}
            />
          </div>
          {resultados.length > 0 && (
            <ul className="resultados" aria-label="Resultados de la búsqueda">
              {resultados.map((p) => (
                <li key={p.legajo}>
                  <button type="button" onClick={() => alElegir(p)}>
                    <UserRound aria-hidden="true" size={16} />
                    {p.nombre} ({p.legajo})
                  </button>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
      {error && <ErrorCampo>{error}</ErrorCampo>}
    </div>
  );
}
