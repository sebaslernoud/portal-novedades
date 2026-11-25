// Formulario de cada tipo de solicitud.
import type { DatosPorTipo, Errores, TipoSolicitud } from '../api/tipos';
import CambioTurno from './CambioTurno';
import FrancoAutorizado from './FrancoAutorizado';
import FrancoCompensatorio from './FrancoCompensatorio';
import LicenciaEspecial from './LicenciaEspecial';
import RetiroIngreso from './RetiroIngreso';

type Props = {
  tipo: TipoSolicitud;
  datos: DatosPorTipo[TipoSolicitud];
  errores: Errores;
  cambiar: (parcial: Partial<DatosPorTipo[TipoSolicitud]>) => void;
};

// El tipo y los datos siempre viajan juntos (se crean con datosIniciales(tipo)).
export function FormularioDeTipo({ tipo, datos, errores, cambiar }: Props) {
  switch (tipo) {
    case 'retiro_ingreso':
      return <RetiroIngreso datos={datos as DatosPorTipo['retiro_ingreso']} errores={errores} cambiar={cambiar} />;
    case 'licencia_especial':
      return (
        <LicenciaEspecial datos={datos as DatosPorTipo['licencia_especial']} errores={errores} cambiar={cambiar} />
      );
    case 'franco_compensatorio':
      return (
        <FrancoCompensatorio
          datos={datos as DatosPorTipo['franco_compensatorio']}
          errores={errores}
          cambiar={cambiar}
        />
      );
    case 'franco_autorizado':
      return (
        <FrancoAutorizado datos={datos as DatosPorTipo['franco_autorizado']} errores={errores} cambiar={cambiar} />
      );
    case 'cambio_turno':
      return <CambioTurno datos={datos as DatosPorTipo['cambio_turno']} errores={errores} cambiar={cambiar} />;
  }
}
