# CLAUDE.md — Portal de Novedades

Portal web para que los empleados **soliciten novedades de personal** (retiros/ingresos fuera de horario, licencias especiales, francos, cambios de turno y cambios de horario). Cada solicitud recorre un **circuito de aprobación** (compañero si corresponde → jefe → RR.HH.) y las aprobadas se exportan a un **Excel de carga masiva para GMS RRHH**, con el mismo formato que hoy genera `proyecto-auto-sc`.

Reemplaza a los formularios en papel que hoy se escanean y se leen con IA en `../proyecto-auto-sc` (Node.js, en producción). Los dos sistemas van a convivir durante la transición.

**Estado:** esqueleto inicial. Corre con Docker y tiene `/api/salud`, una pantalla de estado y la migración base. Todavía no hay modelos de negocio, login ni formularios. Las reglas heredadas están documentadas pero sin portar.

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
docker compose down -v                                       # bajar y BORRAR la base local
```
- Frontend: http://localhost:5173. API: http://localhost:5000/api/salud.
- En desarrollo Vite redirige `/api` al backend, así que el front siempre llama a rutas relativas `/api/...`.
- Antes de dar algo por terminado: los tests y el lint de los dos lados en verde.

## Estructura
```text
backend/
  app/__init__.py      crear_app(): fábrica de Flask
  app/config.py        variables de entorno
  app/db.py            Base declarativa, sesión por petición (sesion)
  app/api/             blueprint /api (una ruta por módulo: salud.py, ...)
  app/modelos/         modelos SQLAlchemy (importarlos en __init__ para Alembic)
  app/reglas/          motor de reglas: solicitud aprobada → filas GMS (A PORTAR)
  app/excel/           Excel de 16 columnas para GMS (A PORTAR)
  migrations/          Alembic (versions/AAAAMMDD_rev_slug.py)
  tests/               pytest
frontend/src/
  api/                 cliente de la API (fetch tipado)
  App.tsx, main.tsx
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
- **Hosting de producción:** probablemente Google Cloud Run + Cloud SQL, como `proyecto-auto-sc`, pero no está decidido.

## Datos sensibles
Las solicitudes contienen datos personales y, en las licencias, datos de salud (Ley 25.326).
- Nunca loguear nombres, legajos, fechas de solicitudes ni contenido de adjuntos.
- Nunca commitear `.env`, credenciales ni datos reales. Para pruebas, usar datos ficticios.
- Cada acción del circuito queda auditada: quién, cuándo, qué y motivo.
