import { screen } from '@testing-library/react';
import { renderizarApp, simularApi } from './pruebas/utilidades';

describe('App', () => {
  afterEach(() => vi.restoreAllMocks());

  it('sin usuario pide elegir uno y muestra el estado del sistema', async () => {
    simularApi({ 'GET /api/salud': { estado: 'ok', base_de_datos: 'ok', migracion: '0002' } });

    renderizarApp('/', null);

    expect(await screen.findByText(/elegí un usuario de prueba/)).toBeInTheDocument();
    expect(await screen.findByText('Backend: funcionando')).toBeInTheDocument();
    expect(screen.queryByRole('navigation')).not.toBeInTheDocument();
  });

  it('avisa si no puede conectar con el backend', async () => {
    simularApi({ 'GET /api/salud': new Response('', { status: 500 }) });

    renderizarApp('/', null);

    expect(await screen.findByText(/No se pudo conectar con el backend/)).toBeInTheDocument();
  });

  it('muestra la exportación solo a RR.HH.', async () => {
    simularApi({ 'GET /api/solicitudes': { mias: [], donde_participo: [] } });

    const { unmount } = renderizarApp('/', 1001);
    expect(await screen.findByText('Todavía no hiciste ninguna solicitud.')).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'Exportación GMS' })).not.toBeInTheDocument();
    unmount();

    renderizarApp('/', 3001);
    expect(await screen.findByRole('link', { name: 'Exportación GMS' })).toBeInTheDocument();
  });
});
