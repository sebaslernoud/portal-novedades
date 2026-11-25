import { useEffect, useState } from 'react';
import type { Persona } from '../api/tipos';
import { listarJefes } from '../api/usuarios';
import { CampoSelector } from './Campos';

type Props = { valor: number | null; error?: string; excluir?: number | null; alCambiar: (legajo: number | null) => void };

export default function SelectorJefe({ valor, error, excluir, alCambiar }: Props) {
  const [jefes, setJefes] = useState<Persona[]>([]);

  useEffect(() => {
    listarJefes()
      .then(setJefes)
      .catch(() => setJefes([]));
  }, []);

  return (
    <CampoSelector
      etiqueta="Jefe que aprueba"
      obligatorio
      valor={valor === null ? '' : String(valor)}
      error={error}
      opciones={jefes
        .filter((j) => j.legajo !== excluir)
        .map((j) => ({ valor: String(j.legajo), nombre: `${j.nombre} (${j.legajo})` }))}
      alCambiar={(v) => alCambiar(v ? Number(v) : null)}
    />
  );
}
