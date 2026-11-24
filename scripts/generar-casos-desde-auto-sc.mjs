// Regenera docs/casos-de-prueba-reglas.json y los Excel de referencia a partir del motor de reglas
// de proyecto-auto-sc (Node.js). Uso, desde la raíz de portal-novedades:
//   node scripts/generar-casos-desde-auto-sc.mjs ../proyecto-auto-sc docs
// Requiere haber corrido npm install en proyecto-auto-sc y que tenga su .env (config.js lo valida).
import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const INICIO = process.cwd();
const ORIGEN = path.resolve(process.argv[2] ?? '../proyecto-auto-sc');
const R = pathToFileURL(ORIGEN + '/src/').href;
process.chdir(ORIGEN);
process.loadEnvFile?.('.env');
const { reglaRetiroIngreso } = await import(R + 'reglas/retiroIngreso.js');
const { reglaLicenciaEspecial } = await import(R + 'reglas/licenciaEspecial.js');
const { reglaFrancoCompensatorio } = await import(R + 'reglas/francoCompensatorio.js');
const { reglaFrancoAutorizado } = await import(R + 'reglas/francoAutorizado.js');
const { reglaCambioTurno } = await import(R + 'reglas/cambioTurno.js');
const { reglaVacaciones } = await import(R + 'reglas/vacaciones.js');
const { generarExcel } = await import(R + 'excel/generarExcel.js');
const { formatear } = await import(R + 'util/fechas.js');

const HOY = { a: 2026, m: 11, d: 24 };
const OUT = path.resolve(INICIO, process.argv[3] ?? 'docs');
const COMMIT = execSync('git rev-parse --short HEAD', { cwd: ORIGEN }).toString().trim();
const titular = (nombre = 'JUAN PEREZ', legajo = '1234') => ({ rol: 'titular', nombre, legajoTexto: legajo, legajoDudoso: false, sector: null });
const P = (rol, nombre, legajo) => ({ rol, nombre, legajoTexto: legajo, legajoDudoso: false, sector: null });
const base = (tipo, bloque, valor, personas, codigos) => ({
  paginaEnBlanco: false, tipoFormulario: tipo, confianzaTipo: 'alta', tituloFormulario: null, fechaFormulario: null,
  personas, [bloque]: valor, novedad: { nombreEscrito: null, codigosDeducidos: codigos, fundamento: '' },
  dudas: [], inconsistencias: [], resumenContenido: '',
});
const RI = (v, cod) => ['retiro_ingreso_fuera_horario', reglaRetiroIngreso, base('retiro_ingreso_fuera_horario', 'retiroIngreso', { opcionMarcada: 'retirarme', fecha: null, hora: null, horarioLaboralDesde: '09:00', horarioLaboralHasta: '18:00', motivo: null, devoluciones: [], ...v }, [titular()], cod)];
const LE = (v) => ['licencia_especial', reglaLicenciaEspecial, base('licencia_especial', 'licenciaEspecial', { motivoTexto: null, tipoLicencia: 'matrimonio', fechaDesde: null, fechaHasta: null, fechaReintegro: null, cantidadDiasNumero: null, ...v }, [titular()], [41])];
const FC = (v, cod) => ['franco_compensatorio', reglaFrancoCompensatorio, base('franco_compensatorio', 'francoCompensatorio', { fechaFranco: null, horaDesdeFranco: null, horaHastaFranco: null, diasTrabajados: [], francoADeterminar: false, motivo: null, ...v }, [titular()], cod)];
const FA = (v) => ['franco_autorizado', reglaFrancoAutorizado, base('franco_autorizado', 'francoAutorizado', { fechaFranco: null, motivo: null, ...v }, [titular()], [40])];
const CT = (v, personas, cod = [37]) => ['cambio_turno', reglaCambioTurno, base('cambio_turno', 'cambioTurno', { fechaCambio: null, fechaDevolucion: null, ...v }, personas, cod)];
const VA = (v) => ['comunicacion_vacacional', reglaVacaciones, base('comunicacion_vacacional', 'vacaciones', { fechaDesde: null, fechaHasta: null, fechaReintegro: null, cantidadDiasNumero: null, cantidadDiasTexto: null, ...v }, [titular()], [2])];
const sol = P('solicitante', 'JUAN PEREZ', '1234');
const ace = P('aceptante', 'ANA GOMEZ', '5678');

const CASOS = {
  retiro_horas_exactas: RI({ fecha: '25/11/2026', hora: '16:00', motivo: 'Turno médico', devoluciones: [{ fecha: '27/11/2026', horaDesde: '18:00', horaHasta: '20:00' }] }, [26, 28]),
  ingreso_dos_devoluciones: RI({ opcionMarcada: 'ingresar', fecha: '25/11/2026', hora: '11:00', motivo: 'Trámite', devoluciones: [{ fecha: '26/11/2026', horaDesde: '18:00', horaHasta: '19:00' }, { fecha: '27/11/2026', horaDesde: '18:00', horaHasta: '19:00' }] }, [42, 28]),
  retiro_horas_no_cierran: RI({ fecha: '25/11/2026', hora: '16:00', devoluciones: [{ fecha: '27/11/2026', horaDesde: '18:00', horaHasta: '19:00' }] }, [26, 28]),
  retiro_horas_a_favor: RI({ fecha: '25/11/2026', hora: '16:00', devoluciones: [{ fecha: '27/11/2026', horaDesde: '18:00', horaHasta: '21:00' }] }, [26, 28]),
  retiro_devolucion_anterior: RI({ fecha: '25/11/2026', hora: '16:00', devoluciones: [{ fecha: '20/11/2026', horaDesde: '18:00', horaHasta: '20:00' }] }, [26, 28]),
  retiro_sin_devoluciones: RI({ fecha: '25/11/2026', hora: '16:00', motivo: 'Personal' }, [26]),
  retiro_turno_noche: RI({ fecha: '25/11/2026', hora: '04:00', horarioLaboralDesde: '22:00', horarioLaboralHasta: '06:00', devoluciones: [{ fecha: '28/11/2026', horaDesde: '06:00', horaHasta: '08:00' }] }, [26, 28]),
  retiro_hora_fuera_de_horario: RI({ fecha: '25/11/2026', hora: '20:00', devoluciones: [{ fecha: '27/11/2026', horaDesde: '18:00', horaHasta: '20:00' }] }, [26, 28]),
  licencia_matrimonio_ok: LE({ tipoLicencia: 'matrimonio', fechaDesde: '01/12/2026', fechaHasta: '10/12/2026' }),
  licencia_matrimonio_supera_tope: LE({ tipoLicencia: 'matrimonio', fechaDesde: '01/12/2026', fechaHasta: '12/12/2026' }),
  licencia_maternidad_sin_codigo_futuro: LE({ tipoLicencia: 'maternidad', fechaDesde: '01/12/2026', fechaHasta: '28/02/2027' }),
  licencia_examen_hasta_desde_reintegro: LE({ tipoLicencia: 'examen', fechaDesde: '01/12/2026', fechaReintegro: '03/12/2026' }),
  licencia_hasta_anterior_a_desde: LE({ tipoLicencia: 'mudanza', fechaDesde: '10/12/2026', fechaHasta: '05/12/2026' }),
  franco_comp_dos_dias_exacto: FC({ fechaFranco: '30/11/2026', horaDesdeFranco: '09:00', horaHastaFranco: '13:00', diasTrabajados: [{ fecha: '20/11/2026', horaDesde: '18:00', horaHasta: '20:00' }, { fecha: '21/11/2026', horaDesde: '18:00', horaHasta: '20:00' }], motivo: 'Cierre de mes' }, [28, 38]),
  franco_comp_solo_franco: FC({ fechaFranco: '30/11/2026', horaDesdeFranco: '09:00', horaHastaFranco: '18:00' }, [38]),
  franco_comp_solo_dia_futuro: FC({ francoADeterminar: true, diasTrabajados: [{ fecha: '28/11/2026', horaDesde: '07:00', horaHasta: '15:00' }] }, [28]),
  franco_comp_horas_a_favor: FC({ fechaFranco: '30/11/2026', horaDesdeFranco: '09:00', horaHastaFranco: '11:00', diasTrabajados: [{ fecha: '20/11/2026', horaDesde: '18:00', horaHasta: '21:00' }] }, [28, 38]),
  franco_comp_mismo_dia: FC({ fechaFranco: '20/11/2026', horaDesdeFranco: '09:00', horaHastaFranco: '11:00', diasTrabajados: [{ fecha: '20/11/2026', horaDesde: '18:00', horaHasta: '20:00' }] }, [28, 38]),
  franco_autorizado: FA({ fechaFranco: '02/12/2026', motivo: 'Cumpleaños' }),
  cambio_turno_dos_personas: CT({ fechaCambio: '06/12/2026', fechaDevolucion: '10/12/2026' }, [sol, ace]),
  cambio_turno_devolucion_mismo_dia: CT({ fechaCambio: '06/12/2026', fechaDevolucion: '06/12/2026' }, [sol, ace]),
  cambio_turno_misma_persona: CT({ fechaCambio: '06/12/2026', fechaDevolucion: '10/12/2026' }, [sol, P('aceptante', 'Perez Juan', '1234')]),
  cambio_horario_una_persona: CT({ fechaCambio: '06/12/2026' }, [sol, P('aceptante', null, null)], [22]),
  cambio_horario_fechas_distintas: CT({ fechaCambio: '06/12/2026', fechaDevolucion: '09/12/2026' }, [sol], [22]),
  vacaciones: VA({ fechaDesde: '04/01/2027', fechaHasta: '17/01/2027', cantidadDiasNumero: 14 }),
};

const fmt = (f) => (f ? formatear(f) : null);
const salida = [];
const filasCarga = [];
for (const [nombre, [tipo, regla, datos]] of Object.entries(CASOS)) {
  const filas = regla({ datos, pagina: 1, hoy: HOY });
  filasCarga.push(...filas.filter((f) => f.motivos.length === 0));
  salida.push({
    nombre,
    tipoFormulario: tipo,
    hoy: '24/11/2026',
    entrada: datos,
    filasEsperadas: filas.map((f) => ({
      legajo: f.legajo, concepto: f.concepto, cantidad: f.cantidad, fechaDesde: fmt(f.fechaDesde), fechaHasta: fmt(f.fechaHasta),
      observaciones: f.observaciones, anioNovedad: f.anioNovedad, mesNovedad: f.mesNovedad,
      fechaValidarFichadas: fmt(f.fechaValidarFichadas), fechaNov28: fmt(f.fechaNov28), horaDesde: f.horaDesde, horaHasta: f.horaHasta,
      codigoFuturo: f.codigoFuturo, motivos: f.motivos,
    })),
  });
}

fs.writeFileSync(`${OUT}/casos-de-prueba-reglas.json`, JSON.stringify({
  descripcion: 'Casos generados con el motor de reglas de proyecto-auto-sc (JavaScript). Para cada caso: los datos de entrada en el formato que recibe el motor y las filas GMS que produce, con sus motivos de revisión (advertencias). El port a Python tiene que producir exactamente lo mismo. Fecha de hoy fija: 24/11/2026.',
  generadoDesde: `proyecto-auto-sc @ ${COMMIT}`,
  casos: salida,
}, null, 2));
fs.writeFileSync(`${OUT}/Plantilla-GMS-16-columnas.xlsx`, await generarExcel({ carga: [], revisar: [], nombrePdf: 'plantilla' }));
fs.writeFileSync(`${OUT}/Ejemplo-salida-GMS.xlsx`, await generarExcel({ carga: filasCarga, revisar: [], nombrePdf: 'ejemplo' }));
console.log('casos:', salida.length, '| filas de ejemplo en Carga:', filasCarga.length);
for (const c of salida) console.log(' ', c.nombre.padEnd(40), c.filasEsperadas.map((f) => `${f.concepto}${f.motivos.length ? '(R)' : ''}`).join(' '));
