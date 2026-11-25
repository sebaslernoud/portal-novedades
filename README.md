# Portal de Novedades

Web para que los empleados soliciten **licencias especiales, francos, cambios de turno, cambios de horario y retiros o ingresos fuera de horario**. Cada solicitud pasa por el circuito de aprobación (compañero → jefe → RR.HH.) y las aprobadas terminan en un **Excel de carga masiva para GMS RRHH**.

Reemplaza a los formularios en papel que hoy se escanean y se procesan con IA en [proyecto-auto-sc](../proyecto-auto-sc). Hereda de ese proyecto todas las reglas de negocio: cómo se calculan las novedades, los textos de Observaciones y el formato del Excel.

> **Estado:** ya están el motor de reglas y el Excel para GMS, portados de `proyecto-auto-sc` (25/25 casos idénticos), los 5 formularios web con sus advertencias, el circuito de aprobación (compañero → jefe → RR.HH.) y la exportación de las aprobadas. Faltan el login, el padrón y los adjuntos, que dependen de definiciones de RR.HH. y Sistemas.

---

## Stack

| Capa | Tecnologías |
|---|---|
| Backend | Python 3.12, Flask 3, SQLAlchemy 2.0, Alembic, PostgreSQL 16, openpyxl |
| Frontend | React 18, TypeScript, Vite |
| Pruebas y calidad | pytest, ruff, Vitest, Testing Library, ESLint |
| Entorno | Docker Compose |

## Requisitos

- **Docker Desktop**, abierto antes de correr los comandos.
- Opcional, para trabajar fuera de Docker: Python 3.12 y Node.js 22.

## Correr el proyecto

```bash
cp .env.example .env          # opcional: los valores por defecto sirven para desarrollo
docker compose up --build
```

| Servicio | Dirección |
|---|---|
| Frontend | http://localhost:5173 |
| API (salud) | http://localhost:5000/api/salud |
| PostgreSQL | `localhost:5432`, usuario `portal`, contraseña `portal`, base `portal_novedades` |

Al arrancar, el backend aplica las migraciones (`alembic upgrade head`). El frontend muestra "Backend: funcionando" y la migración actual.

- Frontend y backend se recargan solos al guardar cambios.
- Para bajar todo: `docker compose down`. Para borrar también la base local: `docker compose down -v`.

## Probarlo de punta a punta

Todavía no hay login. Arriba a la derecha hay un selector de **usuario de prueba**, con personas ficticias. Elegir una equivale a "entrar" como esa persona.

1. Como empleado (por ejemplo, JUAN PEREZ): **Nueva solicitud** → elegir un formulario → completarlo → **Revisar**. Ahí se ven las advertencias y las novedades que se van a cargar en GMS. Después, **Enviar solicitud**.
2. Si es un cambio de turno, el compañero elegido (por ejemplo, ANA GOMEZ) lo encuentra en **Por aprobar** y lo acepta o lo rechaza.
3. El jefe elegido (MARIA LOPEZ o JORGE MARTINEZ) lo aprueba o lo rechaza con motivo desde **Por aprobar**. En el detalle ve las advertencias y las novedades que se van a cargar.
4. Como RR.HH. (SOFIA RAMIREZ): primero se aprueba desde **Por aprobar** y después se exporta desde **Exportación GMS** → elegir las aprobadas → **Exportar** → **Descargar Excel**.
5. El empleado y el jefe ven la solicitud como **No cargada** hasta que RR.HH. la exporta y como **Cargada** después. "Exportada a GMS" solo lo ve RR.HH.

Para tener aprobadas sin recorrer el circuito: `docker compose exec backend flask sembrar`.

## Pruebas y calidad

```bash
docker compose exec backend pytest
docker compose exec backend ruff check .
docker compose exec frontend npm test
docker compose exec frontend npm run lint
docker compose exec frontend npm run typecheck
```

## Migraciones de la base

```bash
docker compose exec backend alembic revision --autogenerate -m "crear tabla solicitudes"
docker compose exec backend alembic upgrade head
docker compose exec backend alembic downgrade -1
```

Los modelos nuevos se importan en `backend/app/modelos/__init__.py`, para que Alembic los detecte.

## Estructura

```text
backend/     API Flask, modelos, migraciones, motor de reglas y Excel
frontend/    React + TypeScript
docs/        especificación, reglas heredadas, casos de prueba y Excel de referencia
scripts/     herramientas (regenerar los casos de prueba desde proyecto-auto-sc)
.claude/     configuración de Claude Code: agente fullstack-dev
CLAUDE.md    guía del proyecto para Claude Code
```

## Lo que se hereda de proyecto-auto-sc

En `docs/`:

| Archivo | Para qué |
|---|---|
| [REGLAS-DE-NEGOCIO.md](docs/REGLAS-DE-NEGOCIO.md) | Cómo cada solicitud se convierte en novedades (26, 28, 37, 22, 38, 40, 41, 42), textos de Observaciones, advertencias, validaciones y formato del Excel. Es lo que hay que portar a Python. |
| [casos-de-prueba-reglas.json](docs/casos-de-prueba-reglas.json) | 25 casos de entrada → filas esperadas, generados con el motor original. El port tiene que dar idéntico (`backend/tests/test_reglas_heredadas.py`). |
| Especificacion-Tecnica-Formularios-Digitales-RRHH.docx | Actores, permisos, circuito, estados, formularios, pantallas y puntos abiertos. |
| Campos-por-formulario.xlsx | Matriz de campos por formulario y listas de valores. |
| Plantilla-GMS-16-columnas.xlsx / Ejemplo-salida-GMS.xlsx | Formato exacto del Excel que acepta GMS. |

**Regenerar los casos** si cambia una regla en `proyecto-auto-sc`. Requiere `npm install` y `.env` en ese proyecto:

```bash
node scripts/generar-casos-desde-auto-sc.mjs ../proyecto-auto-sc docs
```

## Próximos pasos

1. **Fase 0, definiciones con RR.HH. y Sistemas:**
   - Login de empleados.
   - Origen del padrón de empleados y jefes.
   - Puntos abiertos de la especificación.
   El detalle está en `CLAUDE.md`.
2. ~~Portar las reglas y el Excel a Python~~ (hecho, Fase 1).
3. ~~Solicitudes, auditoría, formularios y exportación a Excel~~ (hecho, Fase 2a, con usuario de prueba).
4. **Login, roles y padrón:** reemplazar `app/identidad.py` y el directorio de prueba.
5. ~~Circuito de aprobación~~ (hecho: aceptar, aprobar y rechazar, con la bandeja "Por aprobar"). Falta cancelar, duplicar y aprobar en lote.
6. **Adjuntos** de las licencias, cuando se defina el hosting.
7. **Piloto** con un sector, en paralelo al papel.
