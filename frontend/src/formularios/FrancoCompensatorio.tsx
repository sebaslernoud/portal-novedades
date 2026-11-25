import type { DatosFrancoCompensatorio } from '../api/tipos';
import { CampoFecha, CampoHora, CampoTexto } from '../componentes/Campos';
import Renglones from '../componentes/Renglones';
import type { PropsFormulario } from './tipos';

export default function FrancoCompensatorio({ datos, errores, cambiar }: PropsFormulario<DatosFrancoCompensatorio>) {
  // "A determinar" deja opcional la fecha del franco. El horario laboral de ese día (las horas que no
  // trabaja) es obligatorio si hay fecha: con eso se controla que cierre con lo trabajado.
  const fechaObligatoria = !datos.franco_a_determinar;
  const horarioObligatorio = Boolean(datos.fecha_franco);

  return (
    <>
      <CampoFecha
        etiqueta="Fecha del franco"
        obligatorio={fechaObligatoria}
        valor={datos.fecha_franco}
        error={errores['datos.fecha_franco']}
        alCambiar={(fecha_franco) => cambiar({ fecha_franco })}
      />
      <div className="fila-campos">
        <CampoHora
          etiqueta="Inicio de tu horario laboral"
          obligatorio={horarioObligatorio}
          valor={datos.hora_desde_franco}
          error={errores['datos.hora_desde_franco']}
          alCambiar={(hora_desde_franco) => cambiar({ hora_desde_franco })}
        />
        <CampoHora
          etiqueta="Fin de tu horario laboral"
          obligatorio={horarioObligatorio}
          valor={datos.hora_hasta_franco}
          error={errores['datos.hora_hasta_franco']}
          alCambiar={(hora_hasta_franco) => cambiar({ hora_hasta_franco })}
        />
      </div>
      <p className="nota">Las horas que no vas a trabajar el día del franco. Puede cruzar la medianoche.</p>
      <label className="casilla">
        <input
          type="checkbox"
          checked={datos.franco_a_determinar}
          onChange={(e) => cambiar({ franco_a_determinar: e.target.checked })}
        />
        Fecha del franco a determinar con la jefatura
      </label>
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
