# SmartBancs App

MVP de una plataforma bancaria desarrollado para el reto técnico **TCS NextGen Engineers**.

El proyecto demuestra el diseño e implementación de una plataforma capaz de procesar transferencias bancarias bajo concurrencia, mantener consistencia transaccional, desacoplar la integración con un sistema bancario legado mediante el patrón **Outbox**, procesar recomendaciones de Inteligencia Artificial de forma asíncrona e incorporar observabilidad y pruebas de carga.

---

# 1. ¿Qué demuestra el proyecto?

El MVP integra los siguientes conceptos:

* API REST para operaciones bancarias.
* PostgreSQL como base de datos transaccional.
* Control de concurrencia mediante bloqueo de filas.
* Prevención de transferencias duplicadas mediante idempotencia.
* Patrón **Transactional Outbox**.
* Worker independiente para integración con Bancs.
* Bancs Mock para simular el sistema legado.
* Reintentos ante errores temporales de Bancs.
* Procesamiento de IA desacoplado mediante un AI Worker.
* Integración con Google Gemini.
* Procesamiento ETL con Python y Pandas.
* Métricas HTTP mediante Prometheus.
* Visualización mediante Grafana.
* Pruebas automatizadas y concurrentes.
* Pruebas de carga mediante Locust.
* Ejecución de los servicios mediante Docker Compose.

El objetivo no es presentar una plataforma bancaria lista para producción, sino demostrar criterios de arquitectura, desarrollo, integración, concurrencia, observabilidad y escalabilidad.

---

# 2. Arquitectura


Flujo principal:

```text
Cliente
   │
   ▼
FastAPI
   │
   ▼
PostgreSQL
   │
   ├── Transaction
   │
   └── Outbox Event
          │
          ▼
        Worker
          │
          ▼
      Bancs Mock
```

Procesamiento adicional:

```text
PostgreSQL ──► AI Worker ──► Gemini API
     │
     └────────► Prometheus ──► Grafana
```

El procesamiento de Bancs y de Inteligencia Artificial se mantiene fuera del camino crítico de la transferencia.

---

# 3. Tecnologías

| Componente        | Tecnología              |
| ----------------- | ----------------------- |
| Backend           | Python + FastAPI        |
| ORM               | SQLAlchemy              |
| Validación        | Pydantic                |
| Base de datos     | PostgreSQL 16           |
| Integración Bancs | Outbox + Worker         |
| Bancs             | Bancs Mock              |
| IA                | Google Gemini API       |
| ETL               | Python + Pandas         |
| Métricas          | Prometheus              |
| Dashboards        | Grafana                 |
| Pruebas           | Pytest                  |
| Carga             | Locust                  |
| Contenedores      | Docker + Docker Compose |

---

# 4. Requisitos

Antes de ejecutar el proyecto se necesita:

* Git.
* Python 3.11 o superior.
* Docker Desktop.
* Docker Compose.
* Una API Key de Google Gemini para ejecutar el AI Worker.

Comprobar las instalaciones:

```bash
git --version
python --version
docker --version
docker compose version
```

---

# 5. Instalación

## 5.1 Clonar el repositorio

```bash
git clone https://github.com/EAllaucaD/Reto_SmartBancs.git
cd Reto_SmartBancs
```

## 5.2 Configurar variables de entorno

Crear `.env` a partir del archivo de ejemplo.

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### Linux / macOS

```bash
cp .env.example .env
```

Editar `.env`:

```env
POSTGRES_DB=smartbancs
POSTGRES_USER=smartbancs
POSTGRES_PASSWORD=change_me

PGADMIN_DEFAULT_EMAIL=admin@smartbancs.com
PGADMIN_DEFAULT_PASSWORD=change_me

MOCK_ERROR=

GEMINI_API_KEY=your_gemini_api_key_here
```

`MOCK_ERROR` debe permanecer vacío para el funcionamiento normal.

Valores disponibles para pruebas:

```text
503
```

La API Key de Gemini debe mantenerse únicamente en `.env`.

**No se debe subir `.env` al repositorio.**

---

# 6. Levantar los servicios

Desde la raíz del proyecto:

```bash
docker compose up -d --build
```

Comprobar el estado:

```bash
docker compose ps
```

Para consultar los logs:

```bash
docker compose logs -f
```

Logs de servicios específicos:

```bash
docker compose logs -f worker
```

```bash
docker compose logs -f ai-worker
```

```bash
docker compose logs -f bancs-mock
```

Docker Compose levanta:

* PostgreSQL.
* pgAdmin.
* Bancs Mock.
* Worker.
* AI Worker.
* Prometheus.
* Grafana.

FastAPI se ejecuta actualmente desde el entorno Python local.

---

# 7. Ejecutar FastAPI

Crear el entorno virtual:

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```powershell
pip install -r backend/requirements.txt
```

Ejecutar:

```powershell
uvicorn backend.app.main:app --reload --port 8000
```

La API estará disponible en:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

Redoc:

```text
http://localhost:8000/redoc
```

> El entorno `.venv` solamente se utiliza para ejecutar FastAPI y scripts Python. Docker Compose funciona independientemente del estado del entorno virtual.

---

# 8. Servicios disponibles

| Servicio      | Dirección                | Uso                     |
| ------------- | ------------------------ | ----------------------- |
| FastAPI       | `localhost:8000`         | API principal           |
| Swagger       | `localhost:8000/docs`    | Pruebas de API          |
| Metrics       | `localhost:8000/metrics` | Métricas                |
| Bancs Mock    | `localhost:8001`         | Sistema legado simulado |
| Bancs Swagger | `localhost:8001/docs`    | Pruebas del Mock        |
| PostgreSQL    | `localhost:5432`         | Base de datos           |
| pgAdmin       | `localhost:5050`         | Administración BD       |
| Prometheus    | `localhost:9090`         | Métricas                |
| Grafana       | `localhost:3000`         | Dashboards              |
| Locust        | `localhost:8089`         | Pruebas de carga        |

---

# 9. Uso básico

## Health Check

```http
GET /health
```

Respuesta:

```json
{
  "status": "ok"
}
```

## Health Check de PostgreSQL

```http
GET /health/db
```

Respuesta:

```json
{
  "status": "ok",
  "database": "connected"
}
```

---

## Cuentas

Consultar cuentas:

```http
GET /accounts/
```

Crear una cuenta:

```http
POST /accounts/
```

Ejemplo:

```json
{
  "account_number": "1000000001",
  "customer_ref": "CUSTOMER-001",
  "initial_balance": 1000,
  "currency": "USD"
}
```

El backend controla el saldo inicial y evita cuentas duplicadas.

---

# 10. Transferencias

Crear una transferencia:

```http
POST /transactions/
```

Ejemplo:

```json
{
  "source_account_id": "UUID_ORIGEN",
  "destination_account_id": "UUID_DESTINO",
  "amount": 100
}
```

La solicitud debe incluir:

```text
Idempotency-Key: transfer-001
```

El flujo transaccional es:

```text
Validación
    ↓
Idempotencia
    ↓
Bloqueo de cuentas
    ↓
Validación de saldo
    ↓
Débito / Crédito
    ↓
Crear Transaction
    ↓
Crear Outbox Event
    ↓
COMMIT
```

La transferencia y el evento Outbox se confirman dentro de la misma transacción de PostgreSQL.

---

# 11. Concurrencia e idempotencia

Para evitar condiciones de carrera se utilizan transacciones de PostgreSQL y bloqueo de filas:

```sql
SELECT ...
FROM accounts
WHERE id = ...
FOR UPDATE;
```

Cuando una transferencia involucra dos cuentas, estas se bloquean siguiendo un orden determinista para reducir el riesgo de deadlocks.

La idempotencia se controla mediante `Idempotency-Key`.

Una misma clave no debe crear una segunda transferencia.

---

# 12. Outbox y Bancs

El patrón Outbox permite separar la transferencia de la comunicación con el sistema legado.

```text
FastAPI
   │
   ▼
PostgreSQL
   │
   ▼
Outbox Event
   │
   ▼
Worker
   │
   ▼
Bancs Mock
```

El Worker procesa eventos `PENDING` y utiliza:

```sql
FOR UPDATE SKIP LOCKED
```

para evitar que varios Workers procesen simultáneamente el mismo evento.

Los errores recuperables utilizan reintentos:

```text
Fallo 1 → 2 segundos
Fallo 2 → 4 segundos
Fallo 3 → FAILED
```

Bancs Mock permite simular respuestas HTTP `400`, `500` y `503`.

---

# 13. Inteligencia Artificial

El procesamiento de IA se realiza mediante un Worker independiente:

```text
Datos
  ↓
AI Worker
  ↓
Gemini API
  ↓
ai_recommendations
```

La IA no bloquea la transferencia bancaria.

La transferencia puede completarse aunque Gemini no esté disponible.

---

# 14. ETL

El proyecto incluye un proceso ETL independiente:

```text
Datos RAW
   ↓
Pandas / ETL
   ↓
Datos limpios
   +
Datos rechazados
```

Ejecutar:

```bash
python etl/etl.py
```

Archivos generados:

```text
etl/data/processed/transactions_clean.csv
etl/data/processed/transactions_rejected.csv
```

La exploración de datos se encuentra en:

```text
etl/notebooks/exploracion_data.ipynb
```

---

# 15. Observabilidad

FastAPI expone métricas en:

```text
http://localhost:8000/metrics
```

Prometheus las recopila y Grafana permite visualizarlas.

Se pueden observar, entre otras:

* número de solicitudes;
* solicitudes por endpoint;
* códigos HTTP;
* tasa de solicitudes;
* duración de solicitudes;
* latencia promedio;
* P95 de latencia.

---

# 16. Pruebas

## Prueba de concurrencia

Ejecutar:

```bash
python test_concurrency.py
```

Esta prueba realiza transferencias concurrentes y verifica la consistencia de los saldos.

---

## Prueba de carga

Instalar Locust:

```bash
pip install locust
```

Ejecutar:

```bash
locust -f load_test.py
```

Abrir:

```text
http://localhost:8089
```

En las pruebas locales se obtuvieron como referencia:

```text
30 usuarios concurrentes
827 transacciones
0 errores
41.5 transacciones/segundo
P95 = 1.9 segundos
```

Al aumentar la concurrencia a 40 usuarios, el P95 observado fue de aproximadamente 2.8 segundos.

Estos resultados corresponden al entorno local utilizado durante el desarrollo. **No representan una capacidad demostrada de 10.000 TPS.**

El objetivo de 10.000 TPS se aborda como requisito de escalabilidad mediante una arquitectura que podría distribuir la carga entre múltiples instancias de API y Workers, junto con una infraestructura y base de datos adecuadamente dimensionadas.

---

# 17. Estructura del proyecto

```text
Reto_SmartBancs/
│
├── backend/             # API FastAPI
├── worker/              # Worker de Outbox/Bancs
├── bancs-mock/          # Simulación de Bancs
├── ai-worker/           # Procesamiento de IA
├── etl/                 # Procesamiento ETL
├── monitoring/          # Configuración Prometheus
├── database/            # Recursos de BD
├── load_test.py         # Prueba de carga
├── test_concurrency.py  # Prueba concurrente
├── docker-compose.yml
├── .env.example
├── .gitignore
└── Readme.md
```

---

# 18. Detener el proyecto

Detener los servicios:

```bash
docker compose down
```

Para eliminar también los datos persistidos:

```bash
docker compose down -v
```

> `docker compose down -v` elimina los volúmenes de Docker y, por lo tanto, los datos almacenados en PostgreSQL.

---

# 19. Limitaciones

Este proyecto es un **MVP desarrollado para evaluación técnica**.

Entre sus principales limitaciones:

* Bancs está representado mediante un Mock.
* Las pruebas de carga fueron realizadas en un entorno local.
* Los 10.000 TPS corresponden a un objetivo de escalabilidad, no a una capacidad medida.
* FastAPI se ejecuta actualmente fuera de Docker.
* No se implementa autenticación ni autorización.
* No se implementa alta disponibilidad.
* La API Key de Gemini depende de un servicio externo.

Estos aspectos forman parte de las consideraciones para una implementación productiva.

---

## Referencias

* [FastAPI](https://fastapi.tiangolo.com/)
* [PostgreSQL](https://www.postgresql.org/docs/)
* [Docker Compose](https://docs.docker.com/compose/)
* [Prometheus](https://prometheus.io/docs/)
* [Grafana](https://grafana.com/docs/)
* [Locust](https://docs.locust.io/)
* [Pandas](https://pandas.pydata.org/docs/)
* [Google Gemini API](https://ai.google.dev/)
