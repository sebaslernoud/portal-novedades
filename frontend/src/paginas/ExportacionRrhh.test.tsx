import { fireEvent, screen, within } from '@testing-library/react';
import type { Lote, Solicitud } from '../api/tipos';
import { renderizarApp, respuesta, simularApi } from '../pruebas/utilidades';

function aprobada(id: number, tipo: Solicitud['tipo']): Solicitud {
  return {
    id,
    tipo,
    estado: 'APROBADA',
    solicitante: { legajo: 1001, nombre: 'JUAN PEREZ' },
    jefe: { legajo: 2001, nombre: 'MARIA LOPEZ' },
    jefe_legajo: 2001,
    companero: null,
    datos: {},
    comentario: null,
    advertencias: [],
    creada_en: '2026-11-20T10:00:00-03:00',
    enviada_en: '2026-11-20T10:01:00-03:00',
    lote_exportacion_id: null,
  };
}

const LOTE: Lote = {
  id: 1,
  creado_en: '2026-11-24T12:00:00-03:00',
  usuario: { legajo: 3001, nombre: 'SOFIA RAMIREZ' },
  nombre_archivo: 'Novedades_GMS_20261124-1200.xlsx',
  anio_novedad: 2026,
  mes_novedad: 11,
  cantidad_filas: 3,
  cantidad_solicitudes: 2,
};

describe('Exportación a GMS', () => {
  afterEach(() => vi.restoreAllMocks());

  it('pide confirmación, exporta las elegidas y muestra el lote', async () => {
    let exportado = false;
    const llamadas = simularApi({
      'GET /api/exportaciones/pendientes': () =>
        exportado ? [] : [aprobada(1, 'franco_autorizado'), aprobada(2, 'retiro_ingreso')],
      'GET /api/exportaciones': () => (exportado ? [LOTE] : []),
      'POST /api/exportaciones': () => {
        exportado = true;
        return respuesta(201, LOTE);
      },
    });
    renderizarApp('/exportacion', 3001);

    fireEvent.click(await screen.findByRole('button', { name: 'Exportar 2 solicitudes' }));
    const confirmacion = screen.getByRole('dialog', { name: 'Confirmar exportación' });
    expect(within(confirmacion).getByText(/Exportada a GMS/)).toBeInTheDocument();
    fireEvent.click(within(confirmacion).getByRole('button', { name: 'Confirmar exportación' }));

    expect(await screen.findByText(/Se exportaron 2 solicitudes \(3 novedades\)/)).toBeInTheDocument();
    expect(llamadas.find((l) => l.clave === 'POST /api/exportaciones')?.cuerpo).toEqual({ solicitudes: [1, 2] });
    expect(await screen.findByText('No hay solicitudes aprobadas pendientes de exportar.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Descargar Excel' })).toBeInTheDocument();
  });

  it('se puede destildar una solicitud antes de exportar', async () => {
    simularApi({
      'GET /api/exportaciones/pendientes': [aprobada(1, 'franco_autorizado'), aprobada(2, 'retiro_ingreso')],
      'GET /api/exportaciones': [],
    });
    renderizarApp('/exportacion', 3001);

    fireEvent.click(await screen.findByLabelText('Exportar solicitud 2'));
    expect(screen.getByRole('button', { name: 'Exportar 1 solicitudes' })).toBeInTheDocument();
  });

  it('muestra por qué no se pudo exportar', async () => {
    simularApi({
      'GET /api/exportaciones/pendientes': [aprobada(5, 'retiro_ingreso')],
      'GET /api/exportaciones': [],
      'POST /api/exportaciones': respuesta(422, {
        codigo: 'DATOS_INVALIDOS',
        mensaje: 'Revisá los datos marcados.',
        errores: [{ campo: 'solicitudes.5', mensaje: 'observaciones: Las observaciones tienen 300 caracteres' }],
      }),
    });
    renderizarApp('/exportacion', 3001);

    fireEvent.click(await screen.findByRole('button', { name: 'Exportar 1 solicitudes' }));
    fireEvent.click(screen.getByRole('button', { name: 'Confirmar exportación' }));

    expect(await screen.findByText(/Solicitud 5: observaciones/)).toBeInTheDocument();
  });
});
