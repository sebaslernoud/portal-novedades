import { fireEvent, screen, waitFor } from '@testing-library/react';
import type { Solicitud } from '../api/tipos';
import { renderizarApp, respuesta, simularApi } from '../pruebas/utilidades';

const JEFES = [{ legajo: 2001, nombre: 'MARIA LOPEZ' }];

const ENVIADA: Solicitud = {
  id: 7,
  tipo: 'franco_autorizado',
  estado: 'PENDIENTE_JEFE',
  solicitante: { legajo: 1004, nombre: 'LUCIA FERNANDEZ' },
  jefe: JEFES[0],
  jefe_legajo: 2001,
  companero: null,
  datos: { fecha_franco: '2026-12-02', motivo: 'Cumpleaños' },
  comentario: null,
  advertencias: [],
  creada_en: '2026-11-24T10:00:00-03:00',
  enviada_en: '2026-11-24T10:01:00-03:00',
  lote_exportacion_id: null,
  auditoria: [],
};

async function completarFrancoAutorizado() {
  fireEvent.click(await screen.findByRole('button', { name: /Franco autorizado/ }));
  fireEvent.change(screen.getByLabelText(/^Fecha del franco/), { target: { value: '2026-12-02' } });
  fireEvent.change(screen.getByLabelText(/^Motivo/), { target: { value: 'Cumpleaños' } });
  await screen.findByRole('option', { name: /MARIA LOPEZ/ });
  fireEvent.change(screen.getByLabelText(/^Jefe que aprueba/), { target: { value: '2001' } });
}

describe('Nueva solicitud', () => {
  afterEach(() => vi.restoreAllMocks());

  it('muestra una tarjeta de color por formulario', async () => {
    simularApi({});
    renderizarApp('/nueva', 1004);

    const esperadas: [RegExp, string][] = [
      [/Retiro \/ ingreso/, 'fondo-turquesa'],
      [/Licencia especial/, 'fondo-celeste'],
      [/Franco compensatorio/, 'fondo-lima'],
      [/Franco autorizado/, 'fondo-amarillo'],
      [/Cambio de turno/, 'fondo-azul'],
    ];
    for (const [nombre, color] of esperadas) {
      expect(await screen.findByRole('button', { name: nombre })).toHaveClass('tarjeta-tipo', color);
    }
  });

  it('revisa las advertencias y envía', async () => {
    const llamadas = simularApi({
      'GET /api/usuarios/jefes': JEFES,
      'POST /api/solicitudes/previsualizar': {
        advertencias: ['La fecha 02/12/2027 está a más de 1 año de hoy, confirmar'],
        novedades: [
          {
            legajo: 1004, concepto: 40, cantidad: 1, fecha_desde: '2026-12-02', fecha_hasta: '2026-12-02',
            observaciones: 'Franco autorizado. Cumpleaños', anio_novedad: 2026, mes_novedad: 11,
            fecha_validar_fichadas: null, fecha_nov28: null, hora_desde: null, hora_hasta: null,
            codigo_futuro: null, motivos: [],
          },
        ],
      },
      'POST /api/solicitudes': () => respuesta(201, { ...ENVIADA, estado: 'BORRADOR' }),
      'POST /api/solicitudes/7/enviar': ENVIADA,
      'GET /api/solicitudes/7': ENVIADA,
    }); // prettier-ignore
    renderizarApp('/nueva', 1004);

    await completarFrancoAutorizado();
    fireEvent.click(screen.getByRole('button', { name: 'Revisar' }));

    expect(await screen.findByText(/está a más de 1 año de hoy/)).toBeInTheDocument();
    expect(screen.getByText('Franco autorizado. Cumpleaños')).toBeInTheDocument();
    const previsualizada = llamadas.find((l) => l.clave === 'POST /api/solicitudes/previsualizar');
    expect(previsualizada?.cuerpo).toEqual({
      tipo: 'franco_autorizado',
      jefe_legajo: 2001,
      comentario: '',
      datos: { fecha_franco: '2026-12-02', motivo: 'Cumpleaños' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Enviar solicitud' }));

    expect(await screen.findByText('¡Listo! La solicitud se envió.')).toBeInTheDocument();
    expect(screen.getByText('Esperando al jefe')).toBeInTheDocument();
    expect(llamadas.map((l) => l.clave)).toEqual(
      expect.arrayContaining(['POST /api/solicitudes', 'POST /api/solicitudes/7/enviar']),
    );
  });

  it('muestra los errores de validación del backend', async () => {
    simularApi({
      'GET /api/usuarios/jefes': JEFES,
      'POST /api/solicitudes/previsualizar': respuesta(422, {
        codigo: 'DATOS_INVALIDOS',
        mensaje: 'Revisá los datos marcados.',
        errores: [{ campo: 'datos.fecha_franco', mensaje: 'Completá este campo.' }],
      }),
    });
    renderizarApp('/nueva', 1004);

    fireEvent.click(await screen.findByRole('button', { name: /Franco autorizado/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Revisar' }));

    expect(await screen.findByText('Completá este campo.')).toBeInTheDocument();
    expect(screen.getByText('Revisá los datos marcados.')).toBeInTheDocument();
    expect(screen.getByLabelText(/^Fecha del franco/)).toHaveAttribute('aria-invalid', 'true');
  });

  it('guarda un borrador', async () => {
    const llamadas = simularApi({
      'GET /api/usuarios/jefes': JEFES,
      'POST /api/solicitudes': () => respuesta(201, { ...ENVIADA, estado: 'BORRADOR' }),
      'PUT /api/solicitudes/7': { ...ENVIADA, estado: 'BORRADOR' },
    });
    renderizarApp('/nueva', 1004);

    await completarFrancoAutorizado();
    fireEvent.click(screen.getByRole('button', { name: 'Guardar borrador' }));
    expect(await screen.findByText('Borrador guardado.')).toBeInTheDocument();

    // La segunda vez edita el mismo borrador en lugar de crear otro.
    fireEvent.click(screen.getByRole('button', { name: 'Guardar borrador' }));
    await waitFor(() => expect(llamadas.some((l) => l.clave === 'PUT /api/solicitudes/7')).toBe(true));
    expect(llamadas.filter((l) => l.clave === 'POST /api/solicitudes')).toHaveLength(1);
  });
});
