// Textos para mostrar, ícono y color de cada formulario, y valores iniciales.
import {
  ArrowLeftRight,
  CalendarCheck2,
  CalendarHeart,
  Clock3,
  Stethoscope,
  type LucideIcon,
} from 'lucide-react';
import type { DatosPorTipo, EstadoSolicitud, TipoSolicitud } from './api/tipos';

// Colores de la paleta (ver estilos.css). El rojo no está: queda para errores y alertas.
export type ColorPaleta = 'turquesa' | 'celeste' | 'lima' | 'amarillo' | 'azul';

type DefinicionTipo = { nombre: string; descripcion: string; icono: LucideIcon; color: ColorPaleta };

export const TIPOS: Record<TipoSolicitud, DefinicionTipo> = {
  retiro_ingreso: {
    nombre: 'Retiro / ingreso fuera de horario',
    descripcion: 'Retirarte antes o entrar después de hora un día, y devolver ese tiempo.',
    icono: Clock3,
    color: 'turquesa',
  },
  licencia_especial: {
    nombre: 'Licencia especial',
    descripcion: 'Matrimonio, nacimiento, examen, mudanza y otras licencias.',
    icono: Stethoscope,
    color: 'celeste',
  },
  franco_compensatorio: {
    nombre: 'Franco compensatorio',
    descripcion: 'Un franco a cambio de tareas adicionales que hiciste o vas a hacer.',
    icono: CalendarCheck2,
    color: 'lima',
  },
  franco_autorizado: {
    nombre: 'Franco autorizado',
    descripcion: 'Un franco un día puntual, sin compensar horas.',
    icono: CalendarHeart,
    color: 'amarillo',
  },
  cambio_turno: {
    nombre: 'Cambio de turno',
    descripcion: 'Intercambiar un turno con un compañero.',
    icono: ArrowLeftRight,
    color: 'azul',
  },
};

export const ESTADOS: Record<EstadoSolicitud, string> = {
  BORRADOR: 'Borrador',
  PENDIENTE_COMPANERO: 'Esperando al compañero',
  PENDIENTE_JEFE: 'Esperando al jefe',
  PENDIENTE_RRHH: 'Esperando a RR.HH.',
  APROBADA: 'Aprobada',
  EXPORTADA: 'Exportada a GMS',
  CARGADA_GMS: 'Cargada en GMS',
  ERROR_CARGA: 'Error de carga',
  RECHAZADA: 'Rechazada',
  CANCELADA: 'Cancelada',
};

export const TIPOS_LICENCIA: { valor: string; nombre: string }[] = [
  { valor: 'matrimonio', nombre: 'Matrimonio' },
  { valor: 'pre_matrimoniales', nombre: 'Pre-matrimoniales' },
  { valor: 'nacimiento_adopcion', nombre: 'Nacimiento de hijos / adopción' },
  { valor: 'casamiento_hijos', nombre: 'Casamiento de hijos' },
  { valor: 'dador_sangre', nombre: 'Dador de sangre' },
  { valor: 'mudanza', nombre: 'Mudanza' },
  { valor: 'comparecencia_reparticiones_oficiales', nombre: 'Comparecencia ante reparticiones oficiales' },
  { valor: 'examen', nombre: 'Examen' },
  { valor: 'estudio', nombre: 'Estudio' },
  { valor: 'extraordinaria_sin_goce', nombre: 'Extraordinaria sin goce de haberes' },
  { valor: 'congreso', nombre: 'Congreso' },
  { valor: 'jornada_capacitacion', nombre: 'Jornada de capacitación' },
  { valor: 'festividad', nombre: 'Festividad' },
  { valor: 'maternidad', nombre: 'Maternidad' },
  { valor: 'estado_excedencia', nombre: 'Estado de excedencia' },
];

export function datosIniciales<T extends TipoSolicitud>(tipo: T): DatosPorTipo[T] {
  const iniciales: DatosPorTipo = {
    retiro_ingreso: {
      tipo_movimiento: '',
      fecha: '',
      hora: '',
      horario_laboral_desde: '',
      horario_laboral_hasta: '',
      motivo: '',
      devoluciones: [],
    },
    licencia_especial: { tipo_licencia: '', fecha_desde: '', fecha_hasta: '', fecha_reintegro: '', detalle: '' },
    franco_compensatorio: {
      franco_a_determinar: false,
      fecha_franco: '',
      hora_desde_franco: '',
      hora_hasta_franco: '',
      dias_trabajados: [],
      motivo: '',
    },
    franco_autorizado: { fecha_franco: '', motivo: '' },
    cambio_turno: { companero_legajo: null, fecha_cambio: '', fecha_devolucion: '' },
  };
  return iniciales[tipo];
}

// "2026-11-24" → "24/11/2026"; también acepta fecha y hora ISO ("2026-11-24T10:32:00-03:00").
export function formatearFecha(iso: string | null | undefined): string {
  if (!iso) return '';
  const [anio, mes, dia] = iso.slice(0, 10).split('-');
  return `${dia}/${mes}/${anio}`;
}

export function formatearFechaHora(iso: string | null | undefined): string {
  if (!iso) return '';
  return `${formatearFecha(iso)} ${iso.slice(11, 16)}`;
}

// Días corridos entre dos fechas ISO, inclusive. null si falta alguna o hasta < desde.
export function diasInclusivos(desde: string, hasta: string): number | null {
  if (!desde || !hasta) return null;
  const dias = (Date.parse(`${hasta}T00:00:00Z`) - Date.parse(`${desde}T00:00:00Z`)) / 86_400_000 + 1;
  return dias >= 1 ? dias : null;
}

export function diaAnterior(iso: string): string {
  const fecha = new Date(Date.parse(`${iso}T00:00:00Z`) - 86_400_000);
  return fecha.toISOString().slice(0, 10);
}
