import type { DatosRetiroIngreso } from '../api/tipos';
import { CampoFecha, CampoHora, CampoOpciones, CampoTexto } from '../componentes/Campos';
import Renglones from '../componentes/Renglones';
import type { PropsFormulario } from './tipos';

export default function RetiroIngreso({ datos, errores, cambiar }: PropsFormulario<DatosRetiroIngreso>) {
  return (
    <>
      <CampoOpciones
        destacado
        etiqueta="Tipo"
        obligatorio
        valor={datos.tipo_movimiento}
        error={errores['datos.tipo_movimiento']}
        opciones={[
          { valor: 'retiro', nombre: 'Retiro anticipado' },
          { valor: 'ingreso', nombre: 'Ingreso posterior' },
        ]}
        alCambiar={(v) => cambiar({ tipo_movimiento: v as DatosRetiroIngreso['tipo_movimiento'] })}
      />
      <div className="fila-campos">
        <CampoFecha
          etiqueta="Fecha"
          obligatorio
          valor={datos.fecha}
          error={errores['datos.fecha']}
          alCambiar={(fecha) => cambiar({ fecha })}
        />
        <CampoHora
          etiqueta={datos.tipo_movimiento === 'ingreso' ? 'Hora de ingreso' : 'Hora de retiro'}
          obligatorio
          valor={datos.hora}
          error={errores['datos.hora']}
          alCambiar={(hora) => cambiar({ hora })}
        />
      </div>
      <div className="fila-campos">
        <CampoHora
          etiqueta="Horario laboral desde"
          obligatorio
          valor={datos.horario_laboral_desde}
          error={errores['datos.horario_laboral_desde']}
          alCambiar={(horario_laboral_desde) => cambiar({ horario_laboral_desde })}
        />
        <CampoHora
          etiqueta="Horario laboral hasta"
          obligatorio
          ayuda="Puede cruzar la medianoche (ej. 22:00 a 06:00)."
          valor={datos.horario_laboral_hasta}
          error={errores['datos.horario_laboral_hasta']}
          alCambiar={(horario_laboral_hasta) => cambiar({ horario_laboral_hasta })}
        />
      </div>
      <CampoTexto
        etiqueta="Motivo"
        obligatorio
        valor={datos.motivo}
        error={errores['datos.motivo']}
        alCambiar={(motivo) => cambiar({ motivo })}
      />
      <Renglones
        titulo="Devolución de horas (hasta 4 días)"
        campo="devoluciones"
        renglones={datos.devoluciones}
        errores={errores}
        alCambiar={(devoluciones) => cambiar({ devoluciones })}
      />
    </>
  );
}
