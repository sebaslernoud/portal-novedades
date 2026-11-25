import { fireEvent, screen, waitFor } from '@testing-library/react';
import type { Bandeja, Solicitud } from '../api/tipos';
import { renderizarApp, respuesta, simularApi } from '../pruebas/utilidades';

function solicitud(cambios: Partial<Solicitud>): Solicitud {
  return {
    id: 9,
    tipo: 'franco_autorizado',
    estado: 'PENDIENTE_JEFE',
    solicitante: { legajo: 1001, nombre: 'JUAN PEREZ' },
    jefe: { legajo: 2001, nombre: 'MARIA LOPEZ' },
    jefe_legajo: 2001,
    companero: null,
    datos: { fecha_franco: '2026-12-02', motivo: 'Cumpleaños' },
    comentario: null,
    advertencias: [],
    creada_en: '2026-11-24T10:00:00-03:00',
    enviada_en: '2026-11-24T10:01:00-03:00',
    lote_exportacion_id: null,
    auditoria: [],
    acciones_disponibles: [],
    ...cambios,
  };
}

const VACIA: Bandeja = { companero: [], jefe: [], rrhh: [] };

describe('Circuito de aprobación', () => {
  afterEach(() => vi.restoreAllMocks());

  it('la bandeja muestra solo las secciones con pendientes y el menú las cuenta', async () => {
    simularApi({
      'GET /api/bandeja': { ...VACIA, jefe: [solicitud({}), solicitud({ id: 10 })] },
    });
    renderizarApp('/bandeja', 2001);

    expect(await screen.findByRole('heading', { name: /Para aprobar como jefe/ })).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: /Cambios de turno para aceptar/ })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: /como RR\.HH\./ })).not.toBeInTheDocument();
    expect(screen.getAllByRole('link', { name: /JUAN PEREZ/ })).toHaveLength(2);
    expect(await screen.findByLabelText('2 pendientes')).toBeInTheDocument();
  });

  it('sin pendientes avisa que no hay nada para aprobar', async () => {
    simularApi({ 'GET /api/bandeja': VACIA });
    renderizarApp('/bandeja', 1001);
    expect(await screen.findByText('No tenés nada pendiente de aprobar.')).toBeInTheDocument();
  });

  it('el jefe aprueba desde el detalle y vuelve a la bandeja', async () => {
    const llamadas = simularApi({
      'GET /api/solicitudes/9': solicitud({ acciones_disponibles: ['aprobar', 'rechazar'] }),
      'GET /api/solicitudes/9/novedades': [],
      'POST /api/solicitudes/9/aprobar': solicitud({ estado: 'PENDIENTE_RRHH' }),
      'GET /api/bandeja': VACIA,
    });
    renderizarApp('/solicitudes/9', 2001);

    fireEvent.click(await screen.findByRole('button', { name: 'Aprobar' }));

    expect(await screen.findByText('Aprobaste la solicitud.')).toBeInTheDocument();
    expect(llamadas.some((l) => l.clave === 'POST /api/solicitudes/9/aprobar')).toBe(true);
  });

  it('rechazar exige un motivo antes de llamar al backend', async () => {
    const llamadas = simularApi({
      'GET /api/solicitudes/9': solicitud({ acciones_disponibles: ['aprobar', 'rechazar'] }),
      'GET /api/solicitudes/9/novedades': [],
      'POST /api/solicitudes/9/rechazar': () => respuesta(200, solicitud({ estado: 'RECHAZADA' })),
      'GET /api/bandeja': VACIA,
    });
    renderizarApp('/solicitudes/9', 2001);

    fireEvent.click(await screen.findByRole('button', { name: 'Rechazar' }));
    fireEvent.click(screen.getByRole('button', { name: 'Confirmar rechazo' }));
    expect(screen.getByText(/mínimo 5 caracteres/)).toBeInTheDocument();
    expect(llamadas.some((l) => l.clave === 'POST /api/solicitudes/9/rechazar')).toBe(false);

    fireEvent.change(screen.getByLabelText(/^Motivo del rechazo/), { target: { value: 'Falta personal ese día' } });
    fireEvent.click(screen.getByRole('button', { name: 'Confirmar rechazo' }));

    expect(await screen.findByText('Rechazaste la solicitud.')).toBeInTheDocument();
    expect(llamadas.find((l) => l.clave === 'POST /api/solicitudes/9/rechazar')?.cuerpo).toEqual({
      motivo: 'Falta personal ese día',
    });
  });

  it('el compañero ve "Aceptar cambio"', async () => {
    simularApi({
      'GET /api/solicitudes/9': solicitud({
        tipo: 'cambio_turno',
        estado: 'PENDIENTE_COMPANERO',
        companero: { legajo: 1004, nombre: 'LUCIA FERNANDEZ' },
        acciones_disponibles: ['aprobar', 'rechazar'],
      }),
    });
    renderizarApp('/solicitudes/9', 1004);
    expect(await screen.findByRole('button', { name: 'Aceptar cambio' })).toBeInTheDocument();
  });

  it('sin acciones disponibles no hay panel de decisión', async () => {
    simularApi({ 'GET /api/solicitudes/9': solicitud({ estado: 'NO_CARGADA' }) });
    renderizarApp('/solicitudes/9', 1001);
    expect(await screen.findByText('No cargada')).toBeInTheDocument();
    expect(screen.queryByRole('region', { name: 'Tu decisión' })).not.toBeInTheDocument();
  });

  it('el empleado ve "Cargada" y no la exportación a GMS', async () => {
    simularApi({
      'GET /api/solicitudes': {
        mias: [solicitud({ id: 1, estado: 'CARGADA' }), solicitud({ id: 2, estado: 'NO_CARGADA' })],
        donde_participo: [],
      },
    });
    renderizarApp('/', 1001);
    await waitFor(() => expect(screen.getByText('Cargada')).toBeInTheDocument());
    expect(screen.getByText('No cargada')).toBeInTheDocument();
    expect(screen.queryByText(/Exportada/)).not.toBeInTheDocument();
  });
});
