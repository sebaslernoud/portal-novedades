import { fireEvent, render, screen } from '@testing-library/react';
import { useState } from 'react';
import type { DatosPorTipo, Errores, TipoSolicitud } from '../api/tipos';
import { datosIniciales } from '../textos';
import { FormularioDeTipo } from '.';

function Prueba({ tipo, errores = {} }: { tipo: TipoSolicitud; errores?: Errores }) {
  const [datos, setDatos] = useState<DatosPorTipo[TipoSolicitud]>(datosIniciales(tipo));
  return (
    <FormularioDeTipo
      tipo={tipo}
      datos={datos}
      errores={errores}
      cambiar={(parcial) => setDatos((d) => ({ ...d, ...parcial }) as DatosPorTipo[TipoSolicitud])}
    />
  );
}

const campo = (etiqueta: string) => screen.getByLabelText(new RegExp(`^${etiqueta}( \\*)?$`));

describe('formularios', () => {
  it('retiro / ingreso marca sus obligatorios', () => {
    render(<Prueba tipo="retiro_ingreso" />);
    for (const etiqueta of ['Fecha', 'Hora de retiro', 'Horario laboral desde', 'Horario laboral hasta', 'Motivo']) {
      expect(campo(etiqueta)).toBeRequired();
    }
    expect(screen.getByLabelText('Retiro anticipado')).toBeRequired();
    fireEvent.click(screen.getByLabelText('Ingreso posterior'));
    expect(campo('Hora de ingreso')).toBeInTheDocument();
  });

  it('retiro / ingreso muestra el tipo destacado', () => {
    render(<Prueba tipo="retiro_ingreso" />);
    expect(screen.getByRole('group', { name: /^Tipo/ })).toHaveClass('campo-opciones-destacado');
  });

  it('permite hasta 4 renglones de devolución, cada uno con sus tres datos obligatorios', () => {
    render(<Prueba tipo="retiro_ingreso" />);
    for (let i = 0; i < 4; i++) fireEvent.click(screen.getByRole('button', { name: 'Agregar renglón' }));
    expect(screen.queryByRole('button', { name: 'Agregar renglón' })).not.toBeInTheDocument();
    expect(campo('Fecha 4')).toBeRequired();
    fireEvent.click(screen.getAllByRole('button', { name: 'Quitar' })[0]);
    expect(screen.getByRole('button', { name: 'Agregar renglón' })).toBeInTheDocument();
  });

  it('licencia especial calcula los días y sugiere la fecha hasta desde la reincorporación', () => {
    render(<Prueba tipo="licencia_especial" />);
    expect(campo('Tipo de licencia')).toBeRequired();
    expect(campo('Fecha desde')).toBeRequired();
    expect(campo('Fecha hasta')).toBeRequired();
    expect(campo('Fecha de reincorporación')).not.toBeRequired();
    expect(screen.queryByLabelText(/reintegro/)).not.toBeInTheDocument();

    fireEvent.change(campo('Fecha desde'), { target: { value: '2026-12-01' } });
    fireEvent.change(campo('Fecha de reincorporación'), { target: { value: '2026-12-11' } });

    expect(campo('Fecha hasta')).toHaveValue('2026-12-10');
    expect(screen.getByText('10')).toBeInTheDocument();
  });

  it('franco compensatorio: "a determinar" hace opcional la fecha y el horario laboral depende de la fecha', () => {
    render(<Prueba tipo="franco_compensatorio" />);
    expect(campo('Fecha del franco')).toBeRequired();
    expect(campo('Inicio de tu horario laboral')).not.toBeRequired();

    fireEvent.change(campo('Fecha del franco'), { target: { value: '2026-11-30' } });
    expect(campo('Inicio de tu horario laboral')).toBeRequired();
    expect(campo('Fin de tu horario laboral')).toBeRequired();

    fireEvent.click(screen.getByLabelText(/a determinar/));
    expect(campo('Fecha del franco')).not.toBeRequired();
  });

  it('franco compensatorio: la casilla "a determinar" va entre el horario y los días trabajados', () => {
    render(<Prueba tipo="franco_compensatorio" />);
    const casilla = screen.getByLabelText(/a determinar/);
    const horario = campo('Fin de tu horario laboral');
    const dias = screen.getByRole('group', { name: /Días con tareas adicionales/ });
    expect(horario.compareDocumentPosition(casilla) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(casilla.compareDocumentPosition(dias) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(screen.queryByLabelText(/^Desde/)).not.toBeInTheDocument();
  });

  it('franco autorizado y cambio de turno marcan sus obligatorios', () => {
    const { unmount } = render(<Prueba tipo="franco_autorizado" />);
    expect(campo('Fecha del franco')).toBeRequired();
    expect(campo('Motivo')).not.toBeRequired();
    unmount();

    render(<Prueba tipo="cambio_turno" />);
    expect(campo('Compañero que toma el turno')).toBeRequired();
    expect(campo('Fecha del cambio')).toBeRequired();
    expect(campo('Fecha de devolución')).toBeRequired();
  });

  it('muestra el error del backend junto al campo', () => {
    render(<Prueba tipo="franco_autorizado" errores={{ 'datos.fecha_franco': 'Completá este campo.' }} />);
    expect(campo('Fecha del franco')).toHaveAttribute('aria-invalid', 'true');
    expect(screen.getByRole('alert')).toHaveTextContent('Completá este campo.');
  });
});
