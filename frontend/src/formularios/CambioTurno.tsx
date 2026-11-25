import { useState } from 'react';
import type { DatosCambioTurno, Persona } from '../api/tipos';
import BuscadorCompanero from '../componentes/BuscadorCompanero';
import { CampoFecha } from '../componentes/Campos';
import type { PropsFormulario } from './tipos';

export default function CambioTurno({ datos, errores, cambiar }: PropsFormulario<DatosCambioTurno>) {
  // De un borrador guardado solo se conoce el legajo del compañero.
  const [companero, setCompanero] = useState<Persona | null>(
    datos.companero_legajo ? { legajo: datos.companero_legajo, nombre: 'Legajo' } : null,
  );

  return (
    <>
      <BuscadorCompanero
        seleccionado={companero}
        error={errores['datos.companero_legajo']}
        alElegir={(persona) => {
          setCompanero(persona);
          cambiar({ companero_legajo: persona?.legajo ?? null });
        }}
      />
      <div className="fila-campos">
        <CampoFecha
          etiqueta="Fecha del cambio"
          obligatorio
          ayuda="El día que no trabajás y te cubre tu compañero."
          valor={datos.fecha_cambio}
          error={errores['datos.fecha_cambio']}
          alCambiar={(fecha_cambio) => cambiar({ fecha_cambio })}
        />
        <CampoFecha
          etiqueta="Fecha de devolución"
          obligatorio
          ayuda="El día que vos cubrís a tu compañero. Puede ser antes o el mismo día."
          valor={datos.fecha_devolucion}
          error={errores['datos.fecha_devolucion']}
          alCambiar={(fecha_devolucion) => cambiar({ fecha_devolucion })}
        />
      </div>
    </>
  );
}
