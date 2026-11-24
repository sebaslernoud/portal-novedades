import { render, screen } from '@testing-library/react';
import App from './App';

describe('App', () => {
  afterEach(() => vi.restoreAllMocks());

  it('muestra el estado del backend y de la base', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ estado: 'ok', base_de_datos: 'ok', migracion: '0001' }), { status: 200 }),
    );

    render(<App />);

    expect(await screen.findByText('Backend: funcionando')).toBeInTheDocument();
    expect(screen.getByText('Migración: 0001')).toBeInTheDocument();
  });

  it('avisa si no puede conectar con el backend', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('', { status: 500 }));

    render(<App />);

    expect(await screen.findByText(/No se pudo conectar con el backend/)).toBeInTheDocument();
  });
});
