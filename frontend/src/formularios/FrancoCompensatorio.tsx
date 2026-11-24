import type { DatosFrancoCompensatorio } from '../api/tipos';
import { CampoFecha, CampoHora, CampoTexto } from '../componentes/Campos';
import Renglones from '../componentes/Renglones';
import type { PropsFormulario } from './tipos';

export default function FrancoCompensatorio({ datos, errores, cambiar }: PropsFormulario<DatosFrancoCompensatorio>) {
  // "A determinar" deja opcional la fecha del franco; las horas son obligatorias si hay fecha.
  const fechaObligatoria = !datos.franco_a_determinar;
  const horasObligatorias = Boolean(datos.fecha_franco);

  return (
    <>
      <label className="casilla">
        <input
          type="checkbox"
          checked={datos.franco_a_determinar}
          onChange={(e) => cambiar({ franco_a_determinar: e.target.checked })}
        />
        Fecha del franco a determinar con la jefatura
      </label>
      <div className="fila-campos">
        <CampoFecha
          etiqueta="Fecha del franco"
          obligatorio={fechaObligatoria}
          valor={datos.fecha_franco}
          error={errores['datos.fecha_franco']}
          alCambiar={(fecha_franco) => cambiar({ fecha_franco })}
        />
        <CampoHora
          etiqueta="Desde"
          obligatorio={horasObligatorias}
          valor={datos.hora_desde_franco}
          error={errores['datos.hora_desde_franco']}
          alCambiar={(hora_desde_franco) => cambiar({ hora_desde_franco })}
        />
        <CampoHora
          etiqueta="Hasta"
          obligatorio={horasObligatorias}
          valor={datos.hora_hasta_franco}
          error={errores['datos.hora_hasta_franco']}
          alCambiar={(hora_hasta_franco) => cambiar({ hora_hasta_franco })}
        />
      </div>
      <Renglones
        titulo="Días con tareas adicionales (hasta 4)"
        campo="dias_trabajados"
        renglones={datos.dias_trabajados}
        errores={errores}
        alCambiar={(dias_trabajados) => cambiar({ dias_trabajados })}
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
