// Tipos de la API. Fechas como texto ISO (AAAA-MM-DD) y horas como "HH:MM".

export type Rol = 'empleado' | 'jefe' | 'rrhh';

export type Persona = { legajo: number; nombre: string };

export type Usuario = Persona & { sector: string | null; roles: Rol[] };

export type TipoSolicitud =
  | 'retiro_ingreso'
  | 'licencia_especial'
  | 'franco_compensatorio'
  | 'franco_autorizado'
  | 'cambio_turno';

export type EstadoSolicitud =
  | 'BORRADOR'
  | 'PENDIENTE_COMPANERO'
  | 'PENDIENTE_JEFE'
  | 'PENDIENTE_RRHH'
  | 'APROBADA'
  | 'EXPORTADA'
  | 'CARGADA_GMS'
  | 'ERROR_CARGA'
  | 'RECHAZADA'
  | 'CANCELADA';

// Quien no es RR.HH. no ve la exportación a GMS: el backend le manda NO_CARGADA (aprobada sin
// exportar) o CARGADA (exportada) en lugar del estado real.
export type EstadoVisible = EstadoSolicitud | 'NO_CARGADA' | 'CARGADA';

export type Renglon ={ fecha: string; hora_desde: string; hora_hasta: string };

export type DatosRetiroIngreso = {
  tipo_movimiento: '' | 'retiro' | 'ingreso';
  fecha: string;
  hora: string;
  horario_laboral_desde: string;
  horario_laboral_hasta: string;
  motivo: string;
  devoluciones: Renglon[];
};

export type DatosLicenciaEspecial = {
  tipo_licencia: string;
  fecha_desde: string;
  fecha_hasta: string;
  fecha_reintegro: string;
  detalle: string;
};

export type DatosFrancoCompensatorio = {
  franco_a_determinar: boolean;
  fecha_franco: string;
  hora_desde_franco: string;
  hora_hasta_franco: string;
  dias_trabajados: Renglon[];
  motivo: string;
};

export type DatosFrancoAutorizado = { fecha_franco: string; motivo: string };

export type DatosCambioTurno = {
  companero_legajo: number | null;
  fecha_cambio: string;
  fecha_devolucion: string;
};

export type DatosPorTipo = {
  retiro_ingreso: DatosRetiroIngreso;
  licencia_especial: DatosLicenciaEspecial;
  franco_compensatorio: DatosFrancoCompensatorio;
  franco_autorizado: DatosFrancoAutorizado;
  cambio_turno: DatosCambioTurno;
};

export type CuerpoSolicitud = {
  tipo: TipoSolicitud;
  jefe_legajo: number | null;
  comentario: string;
  datos: DatosPorTipo[TipoSolicitud];
};

export type RegistroAuditoria = {
  usuario: Persona;
  rol: string;
  accion: string;
  estado_anterior: EstadoVisible | null;
  estado_nuevo: EstadoVisible;
  motivo: string | null;
  creado_en: string;
};

export type Solicitud = {
  id: number;
  tipo: TipoSolicitud;
  estado: EstadoVisible;
  solicitante: Persona;
  jefe: Persona | null;
  jefe_legajo: number | null;
  companero: Persona | null;
  datos: Record<string, unknown>;
  comentario: string | null;
  advertencias: string[];
  creada_en: string;
  enviada_en: string | null;
  lote_exportacion_id: number | null;
  auditoria?: RegistroAuditoria[];
  // Solo en el detalle: lo que el usuario actual puede decidir sobre esta solicitud.
  acciones_disponibles?: AccionCircuito[];
};

export type AccionCircuito = 'aprobar' | 'rechazar';

// Lo que cada uno tiene para resolver, según el rol con el que decide.
export type Bandeja = { companero: Solicitud[]; jefe: Solicitud[]; rrhh: Solicitud[] };

export type ListaSolicitudes = { mias: Solicitud[]; donde_participo: Solicitud[] };

export type FilaGms = {
  legajo: number | null;
  concepto: number | null;
  cantidad: number | null;
  fecha_desde: string | null;
  fecha_hasta: string | null;
  observaciones: string | null;
  anio_novedad: number | null;
  mes_novedad: number | null;
  fecha_validar_fichadas: string | null;
  fecha_nov28: string | null;
  hora_desde: string | null;
  hora_hasta: string | null;
  codigo_futuro: number | null;
  motivos: string[];
};

export type Previsualizacion = { advertencias: string[]; novedades: FilaGms[] };

export type Lote = {
  id: number;
  creado_en: string;
  usuario: Persona;
  nombre_archivo: string;
  anio_novedad: number;
  mes_novedad: number;
  cantidad_filas: number;
  cantidad_solicitudes: number;
};

export type ErrorCampo = { campo: string; mensaje: string };

// Errores de validación por campo, con la clave que manda el backend (ej. "datos.fecha").
export type Errores = Record<string, string>;
