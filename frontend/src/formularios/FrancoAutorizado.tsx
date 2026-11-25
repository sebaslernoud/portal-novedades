import type { DatosFrancoAutorizado } from '../api/tipos';
import { CampoFecha, CampoTexto } from '../componentes/Campos';
import type { PropsFormulario } from './tipos';

export default function FrancoAutorizado({ datos, errores, cambiar }: PropsFormulario<DatosFrancoAutorizado>) {
  return (
    <>
      <CampoFecha
        etiqueta="Fecha del franco"
        obligatorio
        valor={datos.fecha_franco}
        error={errores['datos.fecha_franco']}
        alCambiar={(fecha_franco) => cambiar({ fecha_franco })}
      />
      <CampoTexto
        etiqueta="Motivo"
        valor={datos.motivo}
        error={errores['datos.motivo']}
        alCambiar={(motivo) => cambiar({ motivo })}
      />
    </>
  );
}
