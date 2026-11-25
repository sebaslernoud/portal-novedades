// RR.HH.: exportar las solicitudes aprobadas al Excel de GMS y volver a bajar exportaciones anteriores.
import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ErrorApi } from '../api/cliente';
import { descargarExcel, exportar, listarLotes, listarPendientesDeExportar } from '../api/exportaciones';
import type { ErrorCampo, Lote, Solicitud } from '../api/tipos';
import { TIPOS, formatearFecha, formatearFechaHora } from '../textos';

export default function ExportacionRrhh() {
  const [pendientes, setPendientes] = useState<Solicitud[] | null>(null);
  const [lotes, setLotes] = useState<Lote[]>([]);
  const [seleccion, setSeleccion] = useState<Set<number>>(new Set());
  const [confirmando, setConfirmando] = useState(false);
  const [ocupado, setOcupado] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [errores, setErrores] = useState<ErrorCampo[]>([]);
  const [ultimo, setUltimo] = useState<Lote | null>(null);

  const cargar = useCallback(async () => {
    const [aprobadas, anteriores] = await Promise.all([listarPendientesDeExportar(), listarLotes()]);
    setPendientes(aprobadas);
    setSeleccion(new Set(aprobadas.map((s) => s.id)));
    setLotes(anteriores);
  }, []);

  useEffect(() => {
    cargar().catch((e: Error) => setMensaje(e.message));
  }, [cargar]);

  const alternar = (id: number) =>
    setSeleccion((actual) => {
      const nueva = new Set(actual);
      if (nueva.has(id)) nueva.delete(id);
      else nueva.add(id);
      return nueva;
    });

  const confirmar = async () => {
    setOcupado(true);
    setMensaje(null);
    setErrores([]);
    try {
      const lote = await exportar([...seleccion]);
      setUltimo(lote);
      await cargar();
    } catch (e) {
      setMensaje(e instanceof ErrorApi ? e.message : 'No se pudo conectar con el servidor.');
      if (e instanceof ErrorApi) setErrores(e.errores);
    } finally {
      setOcupado(false);
      setConfirmando(false);
    }
  };

  const bajar = (lote: Lote) => descargarExcel(lote).catch((e: Error) => setMensaje(e.message));

  return (
    <section>
      <h1>Exportación a GMS</h1>
      <p className="subtitulo">
        Las solicitudes aprobadas se exportan al Excel de carga masiva. AnioNovedad y mesNovedad toman la fecha de hoy.
      </p>
      {mensaje && (
        <div className="error" role="alert">
          <p>{mensaje}</p>
          {errores.length > 0 && (
            <ul>
              {errores.map((e, i) => (
                <li key={i}>
                  Solicitud {e.campo.replace('solicitudes.', '')}: {e.mensaje}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
      {ultimo && (
        <div className="aviso" role="status">
          Se exportaron {ultimo.cantidad_solicitudes} solicitudes ({ultimo.cantidad_filas} novedades).{' '}
          <button type="button" className="enlace" onClick={() => bajar(ultimo)}>
            Descargar {ultimo.nombre_archivo}
          </button>
        </div>
      )}

      <h2>Aprobadas sin exportar</h2>
      {pendientes === null && <p>Cargando…</p>}
      {pendientes?.length === 0 && <p>No hay solicitudes aprobadas pendientes de exportar.</p>}
      {pendientes && pendientes.length > 0 && (
        <>
          <ul className="lista-solicitudes">
            {pendientes.map((s) => (
              <li key={s.id}>
                <label className="casilla">
                  <input
                    type="checkbox"
                    checked={seleccion.has(s.id)}
                    onChange={() => alternar(s.id)}
                    aria-label={`Exportar solicitud ${s.id}`}
                  />
                  <span>
                    <strong>{TIPOS[s.tipo].nombre}</strong>
                    <span className="detalle-lista">
                      {s.solicitante.nombre} ({s.solicitante.legajo}) · enviada el {formatearFecha(s.enviada_en)}
                      {s.advertencias.length > 0 && ` · ${s.advertencias.length} advertencia(s)`}
                    </span>
                  </span>
                </label>
                <Link to={`/solicitudes/${s.id}`}>Ver</Link>
              </li>
            ))}
          </ul>
          {confirmando ? (
            <div className="confirmacion" role="dialog" aria-label="Confirmar exportación">
              <p>
                ¿Exportar {seleccion.size} solicitudes? Van a pasar a <strong>Exportada a GMS</strong> y no se vuelven
                a exportar.
              </p>
              <div className="acciones">
                <button type="button" className="boton-secundario" onClick={() => setConfirmando(false)} disabled={ocupado}>
                  Cancelar
                </button>
                <button type="button" onClick={confirmar} disabled={ocupado}>
                  Confirmar exportación
                </button>
              </div>
            </div>
          ) : (
            <button type="button" disabled={seleccion.size === 0} onClick={() => setConfirmando(true)}>
              Exportar {seleccion.size} solicitudes
            </button>
          )}
        </>
      )}

      <h2>Exportaciones anteriores</h2>
      {lotes.length === 0 ? (
        <p>Todavía no hay exportaciones.</p>
      ) : (
        <div className="tabla-desplazable">
          <table>
            <thead>
              <tr>
                <th scope="col">Fecha</th>
                <th scope="col">Hecha por</th>
                <th scope="col">Solicitudes</th>
                <th scope="col">Novedades</th>
                <th scope="col">Archivo</th>
              </tr>
            </thead>
            <tbody>
              {lotes.map((lote) => (
                <tr key={lote.id}>
                  <td>{formatearFechaHora(lote.creado_en)}</td>
                  <td>{lote.usuario.nombre}</td>
                  <td>{lote.cantidad_solicitudes}</td>
                  <td>{lote.cantidad_filas}</td>
                  <td>
                    <button type="button" className="enlace" onClick={() => bajar(lote)}>
                      Descargar Excel
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
