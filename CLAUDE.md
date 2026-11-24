# CLAUDE.md — Portal de Novedades

Portal web para que los empleados **soliciten novedades de personal** (retiros/ingresos fuera de horario, licencias especiales, francos, cambios de turno y cambios de horario). Cada solicitud recorre un **circuito de aprobación** (compañero si corresponde → jefe → RR.HH.) y las aprobadas se exportan a un **Excel de carga masiva para GMS RRHH**, con el mismo formato que hoy genera `proyecto-auto-sc`.

Reemplaza a los formularios en papel que hoy se escanean y se leen con IA en `../proyecto-auto-sc` (Node.js, en producción). Los dos sistemas van a convivir durante la transición.

**Estado:** Fase 2a terminada.
- **Fase 1:** el motor de reglas (`app/reglas/`) y el Excel para GMS (`app/excel/`) están portados. Dan idéntico al motor original en los 25 casos.
- **Fase 2a:** hay solicitudes con auditoría, los 5 formularios web (borrador → revisión con advertencias → envío) y la exportación de las APROBADA a un Excel por lote, que se puede volver a bajar idéntico.
- **Sin login ni padrón:** hay un **usuario de prueba** elegido en pantalla (header `X-Legajo-Prueba`) y un directorio ficticio en `app/identidad_prueba.py`.
- **Sin circuito de aprobación:** las solicitudes llegan a APROBADA solo con `flask sembrar`. Tampoco hay adjuntos todavía.

Para el desarrollo, usar el agente **`fullstack-dev`** (`.claude/agents/fullstack-dev.md`).

## Stack
- **Backend:** Python 3.12, Flask 3, SQLAlchemy 2.0 (estilo tipado: `Mapped`, `mapped_column`), Alembic, PostgreSQL 16, openpyxl, pytest y ruff.
- **Frontend:** React 18, TypeScript estricto, Vite, Vitest + Testing Library y ESLint.
- **Infra local:** Docker Compose con tres servicios: `db`, `backend` y `frontend`.

## Comandos
```bash
docker compose up --build                                    # todo el entorno
docker compose exec backend pytest                           # tests del backend
docker compose exec backend ruff check . && docker compose exec backend ruff format --check .
docker compose exec backend alembic revision --autogenerate -m "descripcion"   # nueva migración
docker compose exec backend alembic upgrade head             # aplicar migraciones
docker compose exec frontend npm test                        # tests del frontend
docker compose exec frontend npm run lint
docker compose exec frontend npm run typecheck
docker compose exec backend flask sembrar                    # 5 solicitudes APROBADA ficticias (solo desarrollo)
docker compose down -v                                       # bajar y BORRAR la base local
```
- Los tests del backend usan una base aparte, `portal_novedades_test`, que se crea y migra sola. Cada test corre en una transacción que se deshace al final.
- `IDENTIDAD_DE_PRUEBA=1` (solo en el compose de desarrollo) habilita el usuario de prueba. **Nunca activarlo en producción.**
- Frontend: http://localhost:5173. API: http://localhost:5000/api/salud.
- En desarrollo Vite redirige `/api` al backend, así que el front siempre llama a rutas relativas `/api/...`.
- Antes de dar algo por terminado: los tests y el lint de los dos lados en verde.

## Estructura
```text
backend/
  app/__init__.py      crear_app(): fábrica de Flask
  app/config.py        variables de entorno
  app/db.py            Base declarativa, sesión por petición (sesion)
  app/api/             blueprint /api, un módulo por recurso (solicitudes, exportaciones, usuarios, salud)
                       + serializacion.py (modelos → JSON, fechas ISO)
  app/errores.py       ErrorApi / ErrorValidacion → {"codigo","mensaje","errores"}
  app/identidad.py     usuario_actual(), buscar_persona, listar_jefes: el punto a reemplazar por login y padrón
  app/modelos/         Solicitud, RegistroAuditoria, LoteExportacion, Novedad (importarlos en __init__)
  app/solicitudes/     validacion.py (JSON → entradas del motor), servicio.py (borrador, envío, consulta)
  app/exportacion/     servicio.py: lote todo-o-nada, APROBADA → EXPORTADA, Excel desde las novedades guardadas
  app/reglas/          motor de reglas: generar_filas(solicitud, hoy) → list[FilaNovedad]
                       (entradas.py: solicitudes tipadas; una regla por formulario; motivos.py: textos;
                       advertencias.py: motivos del motor + GEN-1 y RI-4 de la especificación)
  app/excel/           generar_excel(filas) → bytes, validar_fila / separar_validas, nombre_archivo
  app/cli.py           flask sembrar
  migrations/          Alembic (versions/AAAAMMDD_rev_slug.py)
  tests/               pytest (conftest: base de pruebas; casos_heredados.py: adaptador de los 25 casos)
frontend/src/
  api/                 cliente (fetch tipado, ErrorApi, header de usuario de prueba) y tipos.ts
  contexto/Usuario.tsx usuario de prueba elegido en pantalla
  componentes/         campos, renglones, selector de jefe, buscador de compañero, advertencias, tabla GMS
  formularios/         un componente por tipo de solicitud
  paginas/             MisSolicitudes, NuevaSolicitud, DetalleSolicitud, ExportacionRrhh, EstadoSistema
  pruebas/             simularApi() y renderizarApp() para los tests
  textos.ts            nombres, estados, tipos de licencia y formato de fechas
docs/                  especificación, reglas heredadas, casos de prueba, Excel de referencia
scripts/               generar-casos-desde-auto-sc.mjs (regenera los casos desde el motor JS)
```

## Convenciones
- **Código en español**, igual que `proyecto-auto-sc`: tablas, modelos, funciones, variables, rutas y componentes. Ejemplos: `solicitudes`, `Empleado`, `aprobar_solicitud`, `/api/solicitudes`, `BandejaRrhh.tsx`. Se mantienen en inglés las palabras propias de las librerías y frameworks.
- Python: `snake_case`, type hints en todo, funciones chicas y puras en `app/reglas/`, sin lógica de negocio en las rutas.
- TypeScript: `camelCase`, componentes `PascalCase`, sin `any`, tipos de la API en `src/api/`.
- La API devuelve JSON, y los errores con la forma `{"codigo": "...", "mensaje": "..."}`. Los mensajes al usuario van en español rioplatense.
- **Toda modificación de esquema va por Alembic.** No usar `create_all`. Una migración por cambio, revisada a mano después de `--autogenerate`.
- Fechas de negocio como `date`, sin hora, en la zona `America/Argentina/Buenos_Aires`. Horas como `"HH:MM"`.
- Comentarios solo donde aportan el *porqué*, no el qué.

## Dominio (glosario)
- **Novedad:** fila que se carga en GMS (legajo, concepto, fechas, horas, observaciones…).
- **Concepto / código:** 22 cambio de horario, 26 retiro, 28 devolución de horas, 37 cambio de turno, 38 franco compensatorio, 40 franco autorizado, 41 licencia especial (ausencia con aviso), 42 ingreso. El 2 (vacaciones) queda fuera del alcance inicial.
- **Solicitud:** lo que completa el empleado. Una solicitud aprobada genera una o más novedades (por ejemplo, un retiro con dos devoluciones genera un 26 y dos 28; un cambio de turno genera dos 37).
- **Circuito:** Solicitante → (Compañero, solo en el cambio de turno) → Jefe → RR.HH. → Aprobada → Exportada.
- **Advertencias:** los controles de coherencia (horas que no cierran, topes legales, etc.). **No bloquean el envío**: se muestran a los aprobadores.

## Fuentes de verdad (leer antes de implementar)
1. `docs/REGLAS-DE-NEGOCIO.md`: **cómo se calcula cada novedad y el formato del Excel**. Es la lógica heredada y probada de `proyecto-auto-sc`, que hay que portar tal cual.
2. `docs/casos-de-prueba-reglas.json`: 25 casos (entrada → filas esperadas) generados con el motor original. El port a Python tiene que dar **idéntico**. Ver `backend/tests/test_reglas_heredadas.py`.
3. `docs/Especificacion-Tecnica-Formularios-Digitales-RRHH.docx`: actores, permisos, estados, transiciones, datos por formulario, pantallas sugeridas y puntos abiertos.
4. `docs/Campos-por-formulario.xlsx`: matriz formulario × campo (obligatorio, opcional, condicional, automático) y listas de valores.
5. `docs/Plantilla-GMS-16-columnas.xlsx` y `docs/Ejemplo-salida-GMS.xlsx`: el formato exacto de salida.

Si una regla cambia en `proyecto-auto-sc`, regenerar los casos con `node scripts/generar-casos-desde-auto-sc.mjs ../proyecto-auto-sc docs` y volver a correr los tests.

## Decisiones pendientes (Fase 0)
No avanzar con login ni padrón sin estas respuestas de RR.HH. y Sistemas. Preguntarle al usuario si hace falta:
- **Login de empleados:** legajo + contraseña con alta por RR.HH., código por correo o SMS, u otro. No todos los empleados tienen correo. La empresa no usa Google Workspace ni Microsoft 365.
- **Padrón de empleados y jefes:** si se importa de GMS (archivo periódico) o se carga a mano, y cada cuánto se actualiza.
- **Puntos abiertos de la especificación (sección 10):**
  - Qué jefe aprueba en un cambio de turno.
  - Si las solicitudes vencen.
  - Fecha de AnioNovedad y mesNovedad (aprobación o exportación).
  - Cuándo se carga CODIGOFUTURO.
- **Hosting de producción:** probablemente Google Cloud Run + Cloud SQL, como `proyecto-auto-sc`, pero no está decidido. De esto depende dónde se guardan los adjuntos.

Supuestos provisorios que ya están en el código (cambiarlos cuando RR.HH. decida):
- AnioNovedad y mesNovedad salen de la **fecha de exportación**.
- No hay advertencia CT-1: la matriz de campos y el motor permiten devolver el cambio de turno el mismo día.
- La integración con GMS es un Excel por lote que RR.HH. importa a mano. El estado final es `EXPORTADA`.

## Datos sensibles
Las solicitudes contienen datos personales y, en las licencias, datos de salud (Ley 25.326).
- Nunca loguear nombres, legajos, fechas de solicitudes ni contenido de adjuntos.
- Nunca commitear `.env`, credenciales ni datos reales. Para pruebas, usar datos ficticios.
- Cada acción del circuito queda auditada: quién, cuándo, qué y motivo.
