import type { DatosLicenciaEspecial } from '../api/tipos';
import { CampoFecha, CampoSelector, CampoTexto } from '../componentes/Campos';
import { TIPOS_LICENCIA, diaAnterior, diasInclusivos } from '../textos';
import type { PropsFormulario } from './tipos';

export default function LicenciaEspecial({ datos, errores, cambiar }: PropsFormulario<DatosLicenciaEspecial>) {
  const dias = diasInclusivos(datos.fecha_desde, datos.fecha_hasta);

  // Si completa la reincorporación y todavía no puso la fecha hasta, se sugiere el día anterior.
  // El dato se sigue llamando fecha_reintegro, como en el motor heredado.
  const cambiarReintegro = (fecha_reintegro: string) =>
    cambiar(
      fecha_reintegro && !datos.fecha_hasta
        ? { fecha_reintegro, fecha_hasta: diaAnterior(fecha_reintegro) }
        : { fecha_reintegro },
    );

  return (
    <>
      <CampoSelector
        etiqueta="Tipo de licencia"
        obligatorio
        valor={datos.tipo_licencia}
        error={errores['datos.tipo_licencia']}
        opciones={TIPOS_LICENCIA.map((t) => ({ valor: t.valor, nombre: t.nombre }))}
        alCambiar={(tipo_licencia) => cambiar({ tipo_licencia })}
      />
      <div className="fila-campos">
        <CampoFecha
          etiqueta="Fecha desde"
          obligatorio
          valor={datos.fecha_desde}
          error={errores['datos.fecha_desde']}
          alCambiar={(fecha_desde) => cambiar({ fecha_desde })}
        />
        <CampoFecha
          etiqueta="Fecha hasta"
          obligatorio
          ayuda="Último día de licencia, inclusive."
          valor={datos.fecha_hasta}
          error={errores['datos.fecha_hasta']}
          alCambiar={(fecha_hasta) => cambiar({ fecha_hasta })}
        />
        <CampoFecha
          etiqueta="Fecha de reincorporación"
          ayuda="Si la completás, te sugerimos como fecha hasta el día anterior."
          valor={datos.fecha_reintegro}
          error={errores['datos.fecha_reintegro']}
          alCambiar={cambiarReintegro}
        />
      </div>
      <p className="dato-calculado" aria-live="polite">
        Cantidad de días: <strong>{dias ?? '—'}</strong>
      </p>
      <CampoTexto
        etiqueta="Detalle para RR.HH."
        multilinea
        ayuda="Por ejemplo, la institución del examen. No se carga en GMS."
        valor={datos.detalle}
        error={errores['datos.detalle']}
        alCambiar={(detalle) => cambiar({ detalle })}
      />
      <p className="nota">La documentación (acta, certificado) se va a poder adjuntar más adelante.</p>
    </>
  );
}
