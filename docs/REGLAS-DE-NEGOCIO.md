# Reglas de negocio heredadas de proyecto-auto-sc

Este documento reúne **todo lo que ya está resuelto y probado** en el sistema actual de lectura de formularios en papel (`proyecto-auto-sc`, Node.js). Cubre cómo se transforma cada solicitud en **filas de novedades para GMS RRHH** y cómo se arma el **Excel de carga masiva**.

En este proyecto (`portal-novedades`) esa lógica se **reescribe en Python**, en `backend/app/reglas/` y `backend/app/excel/`. Tiene que producir **exactamente** las mismas filas, con los mismos textos, que el motor original. Para verificarlo están los casos de [casos-de-prueba-reglas.json](casos-de-prueba-reglas.json) (sección 13).

> Fuente: `proyecto-auto-sc`, commit indicado en `casos-de-prueba-reglas.json`. Archivos de referencia: `src/reglas/*.js`, `src/util/*.js`, `src/excel/generarExcel.js`, `src/http/excelRoute.js`, `src/config.js`.

---

## 1. Qué cambia y qué no respecto del sistema en papel

| Del sistema actual | En el portal |
|---|---|
| Reglas por formulario: qué filas, qué códigos, qué fechas y horas | **Se portan igual** |
| Textos de Observaciones | **Se portan igual**, carácter por carácter |
| Controles de coherencia (horas que no cierran, topes legales, fechas raras…) | **Se portan**. En el portal son **advertencias** para los aprobadores, no bloquean el envío (decisión de la especificación técnica) |
| Formato del Excel de 16 columnas | **Se porta igual** |
| Validaciones antes de exportar (obligatorios, rangos, 250 caracteres) | **Se portan igual** |
| Lectura con IA, confianza, dudas e inconsistencias de la IA, doble control del código deducido | **No se portan**: no hay papel ni IA |
| Legajo ilegible o dudoso, fecha sin año, horas mal escritas, casillas dudosas | **No se portan**: el formulario web usa campos tipados y el legajo sale del usuario logueado |
| Unificación de cambios de turno repetidos entre páginas | **No se porta**: cada cambio es una única solicitud |
| Hoja "Revisar - no subir" del Excel | **No se porta**: en el portal, lo dudoso se resuelve en el circuito antes de exportar. Solo se exportan solicitudes aprobadas por RR.HH. |

**Entrada de las reglas en el portal:** los datos de una solicitud aprobada, ya tipados (fechas como `date`, horas como `"HH:MM"`, legajos como `int`). En los casos de prueba la entrada está en el formato del motor original (fechas como texto `dd/mm/aaaa`, legajo como texto). El test convierte esos datos al formato del portal antes de llamar a la regla (sección 13).

---

## 2. La fila de novedad

Cada regla devuelve una lista de filas. Una fila tiene:

| Campo | Tipo | Columna GMS | Notas |
|---|---|---|---|
| `legajo` | int | Legajo | |
| `concepto` | int | Concepto | Código de novedad (sección 4) |
| `cantidad` | int | Cantidad | 1, o los días de la licencia o las vacaciones |
| `fecha_desde` | date | FechaDesde | |
| `fecha_hasta` | date | FechaHasta | |
| `observaciones` | str \| None | Observaciones | Máximo 250 para exportar (sección 11) |
| `anio_novedad` | int | AnioNovedad | Ver 3.5 |
| `mes_novedad` | int | mesNovedad | Ver 3.5 |
| `fecha_validar_fichadas` | date \| None | FechaValidarFichadas | Solo en las 28 del franco compensatorio |
| `fecha_nov28` | date \| None | FechaNov28 | Solo en el 37 |
| `hora_desde` | "HH:MM" \| None | HORADESDE | En las 28 |
| `hora_hasta` | "HH:MM" \| None | HORAHASTA | En las 28 |
| `codigo_futuro` | int \| None | CODIGOFUTURO | Solo en el 41 |
| `motivos` | list[str] | — | Advertencias. No van al Excel |

Las columnas `CODIGOMOTIVOHE`, `LEGAJOCOBERTURA` y `CANTIDADHE` existen en el Excel pero **siempre van vacías** (reservadas para uso futuro).

`agregar_motivos(fila, motivos)` agrega cada motivo **sin repetir textos idénticos** y respeta el orden de llegada.

---

## 3. Utilidades

### 3.1 Fechas
- Se trabaja con fechas sin hora (`datetime.date`), nunca con datetimes, para evitar corrimientos de zona horaria.
- `formatear(f)` → `"dd/mm/aaaa"`, con ceros a la izquierda.
- `dias_inclusivos(desde, hasta)` = `(hasta - desde).days + 1`.
- `diferencia_dias(a, b)` = `(b - a).days`.
- Hoy = fecha actual en **America/Argentina/Buenos_Aires**.

### 3.2 Horas
Las horas son texto `"HH:MM"` de 24 horas.
- `minutos(h)` = hh × 60 + mm.
- `duracion_minutos(desde, hasta)`:
  - Si `hasta == desde`, da **0**.
  - Si `hasta > desde`, da la diferencia.
  - Si `hasta < desde`, **cruza la medianoche** (turno noche) y da `hasta + 1440 − desde`.
- `sumar_minutos(hora, n)` → `(hora_resultante "HH:MM", dias_extra)`. `dias_extra` = cuántas veces se pasó la medianoche, `floor(total / 1440)`.
- `formatear_duracion(min)`: `"45 min"`, `"3 h"` o `"2 h 30 min"`.

### 3.3 Textos
- `unir_partes(partes, sep=" ")` une las partes que no son `None` ni vacías.
- `normalizar_observaciones(t)` colapsa espacios (`\s+` → `" "`) y hace `strip`. Si queda vacío, devuelve `None`. **Nunca recorta**.
- `lista_dias(fechas)`: fechas sin repetir, ordenadas.
  - Sin fechas: `None`.
  - Una: `"el día 27/11/2026"`.
  - Varias: `"los días 26/11/2026, 27/11/2026 y 28/11/2026"`.

### 3.4 Constantes (`config.js`)

| Constante | Valor |
|---|---|
| `OBSERVACIONES_MAX_CARACTERES` | 250 |
| `DIAS_MAX_PERIODO` | 60 |
| `DIAS_MAX_ANTIGUEDAD` | 120 |
| `MAX_RENGLONES_DEVOLUCION` | 4 |

### 3.5 AnioNovedad y mesNovedad
Hoy son **el año y el mes de "hoy"** (Buenos Aires) en el momento de generar las filas. En el portal falta decidir si es la fecha de aprobación de RR.HH. o la de exportación: es un punto abierto de la especificación (sección 10). Hasta que se decida, se usa la fecha de exportación, que equivale a "hoy" del motor original.

---

## 4. Códigos de novedad

| Código | Nombre | Lo genera |
|---|---|---|
| 2 | Licencia por vacaciones | Vacaciones (fuera del alcance inicial del portal) |
| 22 | Cambio de horario | Cambio de turno con una sola persona |
| 26 | Retiro antes de hora autorizado | Retiro / ingreso (retiro) |
| 28 | Devolución de horas | Retiro / ingreso, franco compensatorio |
| 37 | Cambio de turno | Cambio de turno (2 filas) |
| 38 | Franco compensatorio | Franco compensatorio |
| 40 | Franco autorizado | Franco autorizado |
| 41 | Ausencia con aviso (todas las licencias especiales) | Licencia especial |
| 42 | Ingreso después de hora autorizado | Retiro / ingreso (ingreso) |

Es la única tabla válida: un concepto que no esté acá no se exporta.

---

## 5. Retiro / ingreso fuera de horario → 26 o 42 + 28

Original: `src/reglas/retiroIngreso.js`, `coherencia.js` (`controlHorasDevolucion`, `separarExcedente`, `controlDevolucionHoras`).

**Entrada:**
- `tipo`: retiro o ingreso.
- `fecha`, `hora`, `horario_laboral_desde`, `horario_laboral_hasta`.
- `motivo` (opcional).
- `devoluciones`: lista de 0 a 4 elementos `{fecha, hora_desde, hora_hasta}`.

**Código:** retiro → **26**, ingreso → **42**.

### 5.1 Fila principal (26/42)
- Cantidad 1, FechaDesde = FechaHasta = `fecha`.
- Encabezado: `"Retiro HH:MM hs."` o `"Ingreso HH:MM hs."`. Sin hora: `"Retiro."` o `"Ingreso."`.
- Observaciones: `unir_partes([encabezado, "Devuelve " + lista_dias(días normales) + "." si hay, motivo])`.
  - Los "días normales" son las fechas de las filas 28 de devolución, **sin** las de horas a favor.
  - Ej.: `Retiro 16:00 hs. Devuelve el día 27/11/2026. Turno médico`
  - Ej.: `Ingreso 11:00 hs. Devuelve los días 26/11/2026 y 27/11/2026. Trámite`
  - Sin devoluciones: `Retiro 16:00 hs. Personal`

### 5.2 Una fila 28 por renglón de devolución
- Cantidad 1, fechas = fecha del renglón, HORADESDE y HORAHASTA del renglón.
- **Ausencia:**
  - Retiro: rango = `hora-laboral_hasta`, o `desde las HH:MM hs` si falta el horario laboral.
  - Ingreso: rango = `laboral_desde-hora`, o `hasta las HH:MM hs`.
  - Texto: `unir_partes(["No trabajó el", formatear(fecha), "<rango> hs"]) + "."`.
- Observaciones: `unir_partes(["Devolución de horas.", ausencia])`.
  - Ej.: `Devolución de horas. No trabajó el 25/11/2026 16:00-18:00 hs.`
- Si falta `hora_hasta`: motivo `Completar HORAHASTA a mano (depende del horario de la persona)`.
- **C5:** si la fecha del renglón es anterior a `fecha`: `La devolución (20/11/2026) es anterior al retiro/ingreso (25/11/2026), confirmar`. Va solo a esa 28.

### 5.3 C12: las horas tienen que cerrar
Se aplica si hay devoluciones:
1. Si algún renglón no tiene alguna de sus horas, no se agrega nada (esa fila ya tiene su propio aviso).
2. Si falta `hora` o el horario laboral, las 28 reciben `No se pudo verificar que las horas de devolución cierren (falta el horario laboral o alguna hora), confirmar`.
3. **Adeudado:**
   - Ingreso: `duracion(laboral_desde, hora)`.
   - Retiro: `duracion(hora, laboral_hasta)`.
4. Si adeudado > `duracion(laboral_desde, laboral_hasta)`:
   - La principal recibe `La hora del retiro/ingreso queda fuera del horario laboral declarado, confirmar`.
   - Las 28 reciben el aviso de "No se pudo verificar…".
   - Se corta acá.
   - Ojo: en este caso la ausencia de las 28 igual se arma con el rango literal (ej. `20:00-18:00 hs`). Es el comportamiento original y el caso de prueba lo refleja.
5. **Devuelto** = suma de `duracion(desde, hasta)` de los renglones.
6. Según el resultado:
   - Devuelto = adeudado: sin aviso.
   - Devuelto < adeudado: todas las 28 reciben `Las horas no cierran: adeuda 2 h y devuelve 1 h, confirmar`.
   - Devuelto > adeudado: **horas a favor** (5.4). Si no se puede separar porque falta alguna fecha u hora, se usa el aviso de C12.

### 5.4 Horas a favor (`separarExcedente`)
1. Los renglones se ordenan por fecha y luego por hora desde.
2. Se recorren acumulando hasta cubrir exactamente el objetivo (lo adeudado):
   - Un renglón que entra entero queda normal.
   - El renglón donde se completa el objetivo **se parte en dos**: el tramo normal termina en `sumar_minutos(desde, restante)` y el tramo a favor empieza ahí. Si el corte pasa la medianoche, la fecha del tramo a favor se corre `dias_extra` días.
   - Los renglones siguientes quedan enteros como a favor.
3. Cada tramo genera su propia fila 28, copiando la del renglón con las fechas y horas del tramo.
4. Las filas a favor llevan:
   - Observaciones: `Horas a favor el 27/11/2026 de 20:00 a 21:00 hs, excedente de la devolución del retiro del 25/11/2026.` (`del ingreso` si es 42).
   - Motivo: `Horas a favor: devuelve 1 h más de lo que adeuda, confirmar si se registran` (minutos a favor = total − objetivo).
5. Las filas normales no reciben aviso de C12.

### 5.5 Otros avisos
- Más de 4 renglones: `El formulario tiene N renglones de devolución y el máximo es 4, confirmar`, a todas las filas. En el portal la UI limita a 4.
- Fechas fuera de ±1 año de hoy: en el portal se valida en el formulario.

**Orden de las filas:** principal, después las 28 en el orden de los tramos.

---

## 6. Licencia especial → 41

Original: `src/reglas/licenciaEspecial.js`.

**Entrada:** `tipo_licencia`, `fecha_desde`, `fecha_hasta`, `fecha_reintegro` (opcional), `cantidad_dias` escrita (opcional) y `motivo` (opcional).

**Fila:**
- FechaDesde = desde.
- FechaHasta = hasta. Si no hay hasta pero sí reintegro: hasta = reintegro − 1 día, con el motivo `FechaHasta deducida de la fecha de reintegro (03/12/2026), confirmar`.
- Cantidad = `dias_inclusivos(desde, hasta)` si hasta ≥ desde. Si no, queda vacía y salta `Falta Cantidad`.
- Observaciones: `Licencia especial: <tipo legible>`.
  - Si el tipo no se identifica: `Licencia especial: <motivo>` (o `Licencia especial`), con el motivo `Tipo de licencia especial no identificado, confirmar`.
- CODIGOFUTURO según la tabla. Si no tiene: motivo `Sin código futuro para este tipo de licencia; completar CODIGOFUTURO a mano`.

| Tipo (valor interno) | Texto legible | CODIGOFUTURO | Tope legal (días) |
|---|---|---|---|
| matrimonio | matrimonio | 4 | 10 (LCT art. 158) |
| pre_matrimoniales | pre-matrimoniales | 39 | — |
| nacimiento_adopcion | nacimiento de hijos/adopción | 8 | 3 (criterio de RR.HH.) |
| casamiento_hijos | casamiento de hijos | 5 | — |
| dador_sangre | dador de sangre | 1 | 1 (Ley 22.990 art. 47) |
| mudanza | mudanza | 13 | — |
| comparecencia_reparticiones_oficiales | comparecencia ante reparticiones oficiales | 12 | — |
| examen | examen | 7 | 10 (LCT art. 158) |
| estudio | estudio | 18 | — |
| extraordinaria_sin_goce | extraordinaria sin goce de haberes | 16 | — |
| congreso | congreso | 30 | — |
| jornada_capacitacion | jornada de capacitación | 43 | — |
| festividad | festividad | 53 | — |
| maternidad | maternidad | — | 90 (LCT art. 177) |
| estado_excedencia | estado de excedencia | — | 184 (LCT art. 183) |

**Controles**, en este orden:
- **C2:** hasta < desde → `FechaHasta anterior a FechaDesde`.
- **C1:** si hay cantidad escrita y ≠ días del período → `El formulario dice X días pero el período son Y días corridos`.
- **C9:** período > 60 días → `Período de N días, inusualmente largo, confirmar`. **No aplica** a maternidad ni a excedencia.
- **C10:** desde hace más de 120 días → `El período comenzó hace más de 120 días, confirmar`.
- **C13:** max(días, cantidad escrita) > tope → `Se piden 12 días de matrimonio y el máximo legal es 10 (LCT art. 158), confirmar`.
- No hay controles sobre el reintegro (pedido de RR.HH.).

---

## 7. Franco compensatorio → 38 + 28

Original: `src/reglas/francoCompensatorio.js`.

**Entrada:**
- `fecha_franco`, `hora_desde_franco`, `hora_hasta_franco`.
- `franco_a_determinar` (bool; se guarda pero no cambia las filas).
- `dias_trabajados`: lista de 0 a 4 elementos `{fecha, hora_desde, hora_hasta}`.
- `motivo` (opcional).

**Qué filas genera:**
- Franco y días trabajados → 38 + una 28 por día.
- Solo franco → solo 38.
- Solo días trabajados → solo las 28.
- Ninguno → una fila 38 vacía con `Formulario de franco sin fecha del franco ni día trabajado; completar a mano`.

**Rango del franco:** `"HH:MM-HH:MM hs"` si hay alguna hora (con `?` en la que falta). Si no hay ninguna, `None`.

**Ausencia:** `unir_partes(["No trabajó el", formatear(fecha_franco), rango]) + "."`. Solo existe si hay fecha de franco.

### 7.1 Fila 38 (si hay fecha de franco)
- Cantidad 1, fechas = franco, **sin** FechaValidarFichadas.
- Observaciones: `unir_partes([unir_partes(["Franco compensatorio", rango]) + ".", "Compensa lo trabajado " + lista_dias(días normales) + "." si hay, motivo])`.
  - Ej.: `Franco compensatorio 09:00-13:00 hs. Compensa lo trabajado los días 20/11/2026 y 21/11/2026. Cierre de mes`

### 7.2 Una fila 28 por día trabajado
- Cantidad 1, fechas = día trabajado, HORADESDE y HORAHASTA del renglón.
- **FechaValidarFichadas** = día trabajado **solo si es hoy o anterior**. Si es futuro: motivo `El día trabajado es futuro; completar a mano una fecha ya trabajada para validar las fichadas`.
- Si falta `hora_hasta`: motivo `Falta HORAHASTA`.
- **Horario trabajado:**
  - `de HH:MM a HH:MM hs` si tiene las dos horas.
  - `desde las HH:MM hs` o `hasta las HH:MM hs` si tiene una.
- Observaciones: `unir_partes([unir_partes(["Devolución de horas por tareas adicionales", "el dd/mm/aaaa", horario]) + ".", ausencia, motivo])`.
  - Ej.: `Devolución de horas por tareas adicionales el 20/11/2026 de 18:00 a 20:00 hs. No trabajó el 30/11/2026 09:00-13:00 hs. Cierre de mes`

### 7.3 Las horas tienen que cerrar
Se aplica si hay franco y días trabajados:
- Si algún renglón no tiene alguna de sus horas, no se agrega nada.
- Si faltan las horas del franco: las 28 reciben `No se pudo verificar que las horas cierren (falta alguna hora del franco o de los días trabajados), confirmar`.
- Si las horas del franco ≠ las trabajadas: las 28 reciben `Las horas no cierran: el franco es de 2 h y lo trabajado suma 3 h, confirmar`.
- Si lo trabajado es mayor: **horas a favor**, con el mismo algoritmo de 5.4 y como objetivo la duración del franco.
  - Observaciones: `Horas a favor el 20/11/2026 de 20:00 a 21:00 hs, excedente de lo trabajado para el franco del 30/11/2026.`
  - Motivo: `Horas a favor: trabajó 1 h más de lo que dura el franco, confirmar si se registran`.
  - Al partir un renglón, cada tramo mantiene FechaValidarFichadas (con la fecha del tramo) si el renglón la tenía.

### 7.4 C6
Si el franco cae el mismo día que algún día trabajado: `El franco y el día trabajado son el mismo día (20/11/2026), confirmar`, a **todas** las filas. Un franco anterior al día trabajado está permitido.

**Orden de las filas:** 38 primero, después las 28.

---

## 8. Franco autorizado → 40

Original: `src/reglas/francoAutorizado.js`.

- **Entrada:** `fecha_franco` y `motivo` (opcional).
- **Fila:** Cantidad 1, fechas = franco.
- **Observaciones:** `unir_partes(["Franco autorizado.", motivo])`.
  - Ej.: `Franco autorizado. Cumpleaños`
- Nunca genera 28 ni 38.

---

## 9. Cambio de turno → 37 × 2, o cambio de horario → 22

Original: `src/reglas/cambioTurno.js`, `coherencia.js` (`controlMismaPersona`).

**Entrada:** `solicitante` y `aceptante` (cada uno con legajo y nombre), `fecha_cambio` y `fecha_devolucion`.

### 9.1 Cambio de horario (22)
Si **exactamente una** de las dos personas tiene datos (nombre o legajo), es un cambio de horario:
- Una fila 22 para esa persona. Cantidad 1, fechas = `fecha_cambio`, sin FechaNov28.
- Observaciones: `Cambio de horario el 06/12/2026.`, o `Cambio de horario.` si no hay fecha.
- Si hay `fecha_devolucion` y es distinta de `fecha_cambio`: motivo `Cambio de horario con fecha de devolución (09/12/2026) distinta del día del cambio (06/12/2026): confirmar si es un cambio de horario o un cambio de turno sin el compañero`.

En el portal conviene que "Cambio de horario" sea **un formulario propio**, con una persona y una fecha, en lugar de un cambio de turno sin compañero. La fila que genera es la misma.

### 9.2 Cambio de turno (37), dos personas
| Fila | Legajo | FechaDesde = FechaHasta | FechaNov28 |
|---|---|---|---|
| 1 | solicitante | fecha_cambio | fecha_devolucion |
| 2 | aceptante | fecha_devolucion | fecha_cambio |

- Cantidad 1 en las dos.
- Observaciones: `unir_partes([f"{propio or '(sin nombre)'} x {otro or '(sin nombre)'}", f"Día del Cambio: {fecha de su fila}" si hay, f"Día de devolución: {su FechaNov28}" si hay], " - ")`.
  - Fila 1: `JUAN PEREZ x ANA GOMEZ - Día del Cambio: 06/12/2026 - Día de devolución: 10/12/2026`
  - Fila 2: `ANA GOMEZ x JUAN PEREZ - Día del Cambio: 10/12/2026 - Día de devolución: 06/12/2026`
- La devolución puede ser **anterior** al cambio o **el mismo día**: no hay aviso.
- **C8:** mismo legajo, o mismo nombre normalizado → `Solicitante y aceptante tienen el mismo legajo o nombre`. El nombre se normaliza así: sin acentos, en minúsculas, solo letras y espacios, con las palabras ordenadas. Por eso "Perez Juan" = "JUAN PEREZ".
- **Agrupación:** si una de las dos filas tiene motivos, la otra recibe `Otra fila del mismo cambio de turno requiere revisión; se revisan las 2 juntas`. Siempre se tratan juntas.
- Un 37 sin FechaNov28 tiene el motivo `Falta FechaNov28`.

---

## 10. Vacaciones → 2 (fuera del alcance inicial)

Original: `src/reglas/vacaciones.js`. Se documenta por si se suma más adelante.
- Cantidad = la cantidad escrita. Si no hay, = días inclusivos, con el motivo `El formulario no indica la cantidad de días; se calcularon N días corridos`.
- Hasta se deduce del reintegro igual que en la licencia.
- Controles: C1, C2, C9 y C10.
- Sin Observaciones.

---

## 11. Campos obligatorios y validaciones antes de exportar

### 11.1 Obligatorios por fila (`verificarObligatorios`)
| Condición | Motivo |
|---|---|
| Legajo vacío | `Falta el legajo` |
| Concepto vacío | `Falta Concepto` |
| Cantidad vacía | `Falta Cantidad` |
| FechaDesde vacía | `Falta FechaDesde` |
| FechaHasta vacía | `Falta FechaHasta` |
| Concepto 28 sin HORADESDE | `Falta HORADESDE` |
| Concepto 37 sin FechaNov28 | `Falta FechaNov28` |

Al final de cada regla, en orden:
1. Obligatorios.
2. Motivos comunes del formulario.
3. Normalizar Observaciones.
4. Si Observaciones tiene más de 250 caracteres: `Observaciones de N caracteres: el máximo de GMS es 250, acortarlas a mano sin perder lo importante`.

### 11.2 Validación de cada fila al exportar (`excelRoute.js`)
| Campo | Regla |
|---|---|
| Legajo | Entero de 1 a 99.999.999 |
| Concepto | Entero que esté en la tabla de códigos |
| Cantidad | Entero de 1 a 999 |
| AnioNovedad | 2000 a 2100 |
| mesNovedad | 1 a 12 |
| CODIGOFUTURO | Entero de 1 a 9999 |
| Fechas | Fecha válida |
| Horas | `HH:MM` válida |
| Observaciones | Máximo 250 caracteres |
| Obligatorios | Los de 11.1 |

Una fila que no pasa la validación no se exporta.

---

## 12. Formato del Excel para GMS

Original: `src/excel/generarExcel.js`. Referencias: [Plantilla-GMS-16-columnas.xlsx](Plantilla-GMS-16-columnas.xlsx) (solo encabezados) y [Ejemplo-salida-GMS.xlsx](Ejemplo-salida-GMS.xlsx) (26 filas generadas con los casos de prueba).

- **Una sola hoja**, llamada **`Novedades a cargar`**. GMS solo acepta una hoja.
- Fila 1: encabezados en negrita, fijos al desplazarse. Desde la fila 2: una fila por novedad.
- **Las celdas sin valor no se escriben**: ni `""`, ni `0`, ni `"null"`.

| Col | Encabezado (exacto) | Tipo de celda | Formato | Ancho |
|---|---|---|---|---|
| A | `Legajo` | número | `0` | 12 |
| B | `Concepto` | número | `0` | 11 |
| C | `Cantidad` | número | `0` | 10 |
| D | `FechaDesde` | fecha real | `dd/mm/yyyy` | 14 |
| E | `FechaHasta` | fecha real | `dd/mm/yyyy` | 14 |
| F | `Observaciones` | texto | — | 50 |
| G | `AnioNovedad` | número | `0` | 13 |
| H | `mesNovedad` | número | `0` | 12 |
| I | `FechaValidarFichadas` | fecha real | `dd/mm/yyyy` | 20 |
| J | `FechaNov28` | fecha real | `dd/mm/yyyy` | 14 |
| K | `HORADESDE` | número (fracción de día) | `hh:mm` | 11 |
| L | `HORAHASTA` | número (fracción de día) | `hh:mm` | 11 |
| M | `CODIGOFUTURO` | número | `0` | 15 |
| N | `CODIGOMOTIVOHE` | número | `0` | 16 |
| O | `LEGAJOCOBERTURA` | número | `0` | 17 |
| P | `CANTIDADHE` | número | `0` | 12 |

- **Fechas:** se escriben como fecha de Excel, sin hora.
- **Horas:** `(hh × 60 + mm) / 1440`.
- **Nombre del archivo** en el original: `Novedades_<base>_<aaaammdd>-<hhmm>.xlsx`. La base son los primeros 40 caracteres del nombre, con lo que no sea letra o número reemplazado por `_`. La hora es la de Buenos Aires.
- En Python: **openpyxl**.

---

## 13. Casos de prueba: [casos-de-prueba-reglas.json](casos-de-prueba-reglas.json)

Son 25 casos generados con el motor original, con hoy fijo en **24/11/2026**. Cubren:
- Retiro / ingreso: horas exactas, dos devoluciones, horas que no cierran, horas a favor, devolución anterior, sin devoluciones, turno noche y hora fuera de horario.
- Licencia especial: ok, supera el tope, maternidad sin código futuro, hasta deducida del reintegro y hasta anterior a desde.
- Franco compensatorio: dos días exactos, solo franco, día futuro, horas a favor y mismo día.
- Franco autorizado.
- Cambio de turno: dos personas, devolución el mismo día y misma persona.
- Cambio de horario: una persona y fechas distintas.
- Vacaciones.

Formato de cada caso:

```json
{
  "nombre": "retiro_horas_exactas",
  "tipoFormulario": "retiro_ingreso_fuera_horario",
  "hoy": "24/11/2026",
  "entrada": { "personas": [...], "retiroIngreso": { ... }, "...": "formato del motor original" },
  "filasEsperadas": [
    { "legajo": 1234, "concepto": 26, "cantidad": 1, "fechaDesde": "25/11/2026", "fechaHasta": "25/11/2026",
      "observaciones": "Retiro 16:00 hs. Devuelve el día 27/11/2026. Turno médico",
      "anioNovedad": 2026, "mesNovedad": 11, "fechaValidarFichadas": null, "fechaNov28": null,
      "horaDesde": null, "horaHasta": null, "codigoFuturo": null, "motivos": [] }
  ]
}
```

**Cómo usarlos:** test parametrizado en `backend/tests/test_reglas_heredadas.py`.
1. Leer el JSON.
2. Convertir `entrada` al formato del portal:
   - `opcionMarcada` `retirarme`/`ingresar` → `tipo`.
   - Fechas `dd/mm/aaaa` → `date`.
   - `legajoTexto` → `int`.
   - En `personas`, el rol `titular` es el solicitante de la solicitud.
3. Llamar a la regla con `hoy = date(2026, 11, 24)`.
4. Comparar **campo por campo y en orden**, incluidos los textos de `observaciones` y la lista `motivos`.

Los motivos son advertencias para el circuito de aprobación del portal, así que su texto puede adaptarse más adelante. Si se cambia, hay que actualizar el caso y registrar la decisión.

> Si alguna regla cambia en `proyecto-auto-sc` mientras convivan los dos sistemas, regenerar este JSON con `scripts/generar-casos-desde-auto-sc.mjs` (ver `README.md`) y volver a correr los tests.
