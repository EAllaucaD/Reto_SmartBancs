# SmartBancs App

MVP de una plataforma bancaria desarrollada como parte de un reto técnico.

El objetivo es construir una aplicación capaz de procesar transferencias bancarias de forma segura, manejar concurrencia, desacoplar la integración con un sistema bancario legado llamado Bancs y procesar recomendaciones de Inteligencia Artificial de forma asíncrona.

El proyecto busca demostrar criterios de:

* Desarrollo de software.
* Diseño de arquitectura.
* Bases de datos transaccionales.
* Concurrencia.
* Integración con sistemas legados.
* Inteligencia Artificial.
* Observabilidad.
* Pruebas.
* Dockerización.
* Seguridad.

---

## 1. Stack tecnológico

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic

### Base de datos

* PostgreSQL

### Contenedores

* Docker
* Docker Compose

### IA

* Gemini API

La API Key se manejará mediante una variable de entorno:

```text
GEMINI_API_KEY
```

Nunca se debe almacenar la clave real en GitHub.

### Datos

* Python
* Pandas

Se utilizará posteriormente para procesos de limpieza y preparación de datos.

### Observabilidad

Se contempla utilizar:

* Logs estructurados.
* Métricas.
* OpenTelemetry.

---

## 2. Estado actual del proyecto

Actualmente se encuentra implementado:

* PostgreSQL mediante Docker Compose.
* pgAdmin.
* Conexión FastAPI → PostgreSQL.
* Endpoint `/health`.
* Endpoint `/health/db`.
* Modelo SQLAlchemy `Account`.
* Endpoint para consultar cuentas.
* Endpoint para crear cuentas.
* Validación mediante Pydantic.
* Manejo de cuentas duplicadas.
* Variables de entorno para la conexión a PostgreSQL.

Endpoints actuales:

```text
GET  /health
GET  /health/db
GET  /accounts/
POST /accounts/
```

---

## 3. Estructura actual

```text
smartbancs-app/
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   └── account.py
│   │   │
│   │   ├── routers/
│   │   │   └── accounts.py
│   │   │
│   │   ├── schemas/
│   │   │   └── account.py
│   │   │
│   │   ├── database.py
│   │   └── main.py
│   │
│   └── requirements.txt
│
├── database/
│
├── .env
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

La estructura crecerá progresivamente conforme se implementen las transacciones, Outbox, Bancs Mock, IA y observabilidad.

## Worker y Bancs Mock

El Worker es un servicio independiente ubicado en `worker/`. Consulta
periódicamente los eventos `PENDING` de `outbox_events`, los reclama con
`FOR UPDATE SKIP LOCKED` y los envía mediante HTTP a `bancs-mock:8000`.

Para errores recuperables utiliza hasta tres intentos:

```text
fallo 1 -> 2 segundos
fallo 2 -> 4 segundos
fallo 3 -> FAILED
```

Los errores HTTP 400 se marcan directamente como `FAILED`. Los eventos
`FAILED` no se eliminan.

Si Bancs Mock responde correctamente y el Worker se detiene antes de confirmar
`PROCESSED`, el evento puede volver a enviarse. La idempotencia externa de Bancs
Mock queda pendiente de una fase posterior; esta implementación no modifica ese
servicio ni agrega persistencia adicional.

---

# 4. Base de datos

La base de datos actual contiene las siguientes tablas:

```text
accounts
transactions
outbox_events
ai_recommendations
```

## accounts

Representa las cuentas bancarias.

Campos principales:

```text
id
account_number
customer_ref
balance
currency
status
created_at
updated_at
```

El saldo inicial es controlado por el backend y no por el cliente de la API.

---

## transactions

Representará las transferencias entre cuentas.

Campos:

```text
id
idempotency_key
source_account_id
destination_account_id
amount
currency
status
created_at
completed_at
```

Estados:

```text
PENDING
COMPLETED
FAILED
```

---

## outbox_events

Almacenará eventos que posteriormente serán procesados por un worker para integrarse con Bancs.

Campos:

```text
id
transaction_id
event_type
payload
status
attempts
next_attempt_at
last_error
created_at
processed_at
```

Estados:

```text
PENDING
PROCESSING
PROCESSED
FAILED
```

---

## ai_recommendations

Almacenará las recomendaciones generadas mediante Inteligencia Artificial.

Campos:

```text
id
account_id
recommendation
model
status
error_message
created_at
updated_at
```

Estados:

```text
PENDING
COMPLETED
FAILED
```

---

# 5. Arquitectura objetivo

La arquitectura final esperada será:

```text
                         ┌──────────────────┐
                         │     Cliente      │
                         │ Postman / HTTP   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         │ Transaction API  │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
             ┌────────────┐ ┌────────────┐ ┌─────────────┐
             │ PostgreSQL │ │   Outbox   │ │ Async AI    │
             │            │ │   Events   │ │ Processing  │
             └────────────┘ └─────┬──────┘ └──────┬──────┘
                                  │               │
                                  ▼               ▼
                           ┌────────────┐  ┌────────────┐
                           │ Bancs      │  │ Gemini API │
                           │ Worker     │  │            │
                           └─────┬──────┘  └────────────┘
                                 │
                                 ▼
                           ┌────────────┐
                           │ Bancs Mock │
                           └────────────┘
```

---

# 6. Bancs

Bancs representa un sistema bancario legado.

No se instalará Bancs real.

Para el MVP se utilizará un Mock de Bancs que permita demostrar la integración.

La arquitectura debe evitar realizar llamadas directas y síncronas a Bancs durante una transferencia.

El flujo esperado será:

```text
SmartBancs
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

Esto permite desacoplar el procesamiento de transferencias del sistema legado.

---

# 7. Flujo de una transferencia

El flujo principal será:

```text
Cliente
   │
   ▼
FastAPI
   │
   ▼
Validación
   │
   ▼
Idempotencia
   │
   ▼
BEGIN
   │
   ▼
Bloqueo de cuentas
   │
   ▼
Verificación de saldo
   │
   ▼
Débito cuenta origen
   │
   ▼
Crédito cuenta destino
   │
   ▼
Crear transaction
   │
   ▼
Crear evento Outbox
   │
   ▼
COMMIT
   │
   ▼
Respuesta
```

La recomendación de IA se procesará posteriormente de forma asíncrona.

---

# 8. Concurrencia

El sistema debe considerar múltiples transferencias ejecutándose simultáneamente.

El problema principal es evitar condiciones de carrera.

Ejemplo:

```text
Saldo = 1000

Transferencia A → 700
Transferencia B → 600
```

Ambas operaciones no deben poder utilizar simultáneamente el mismo saldo disponible.

Para esto se utilizarán transacciones de PostgreSQL y bloqueo de filas.

Conceptualmente:

```sql
SELECT ...
FROM accounts
WHERE id = ...
FOR UPDATE;
```

El orden general será:

```text
BEGIN
   ↓
LOCK
   ↓
Verificar saldo
   ↓
Actualizar cuentas
   ↓
Registrar transferencia
   ↓
Crear Outbox
   ↓
COMMIT
```

---

# 9. Deadlocks

Cuando una transferencia involucre dos cuentas, ambas cuentas deberán bloquearse siguiendo un orden determinista.

Por ejemplo:

```text
UUID menor
    ↓
UUID mayor
```

Esto reduce el riesgo de que dos transacciones bloqueen las mismas cuentas en órdenes diferentes.

---

# 10. Idempotencia

Las transferencias utilizarán:

```text
idempotency_key
```

para evitar que una misma solicitud sea procesada dos veces accidentalmente.

Ejemplo:

```text
Request 1
idempotency_key = ABC123
      ↓
Transferencia creada

Request 2
idempotency_key = ABC123
      ↓
No crear otra transferencia
```

La idempotencia será implementada antes de considerar terminada la lógica de transferencias.

---

# 11. Outbox Pattern

La creación de una transferencia y su evento Outbox deben formar parte de la misma transacción de PostgreSQL.

Conceptualmente:

```text
BEGIN
   │
   ├── Actualizar cuenta origen
   ├── Actualizar cuenta destino
   ├── Crear transaction
   └── Crear outbox_event
          │
          ▼
       COMMIT
```

Si alguna operación falla:

```text
ROLLBACK
```

De esta forma no debe existir una transferencia confirmada sin su evento correspondiente.

---

# 12. Inteligencia Artificial

Las recomendaciones financieras no deben bloquear una transferencia.

El flujo será:

```text
Transferencia
      │
      ▼
COMMIT
      │
      ▼
Procesamiento asíncrono
      │
      ▼
Gemini API
      │
      ▼
ai_recommendations
```

La caída o indisponibilidad de Gemini no debe provocar que una transferencia válida sea revertida.

---

# 13. Seguridad

El proyecto debe considerar desde el desarrollo:

* Validación de entradas.
* Integridad mediante restricciones de PostgreSQL.
* Uso de transacciones.
* Control de concurrencia.
* Idempotencia.
* Manejo seguro de errores.
* No exposición de errores internos.
* Protección de credenciales.
* Variables de entorno para secretos.
* No almacenar `.env` en Git.
* No permitir que el cliente modifique directamente saldos.
* Validación de estados de las cuentas.

El proyecto es un MVP y no debe declararse como listo para producción mientras falten mecanismos como autenticación, autorización, rate limiting y otros controles necesarios.

---

# 14. Roadmap

El desarrollo se realizará progresivamente:

### Fase 1 — Cuentas

* [] Modelo Account.
* [] GET `/accounts/`.
* [] POST `/accounts/`.
* [] Validación Pydantic.
* [] Manejo de duplicados.

### Fase 2 — Transacciones

* [ ] Modelo Transaction.
* [ ] Schemas de Transaction.
* [ ] Endpoint de transferencia.
* [ ] Validación de cuentas.
* [ ] Validación de saldo.
* [ ] Actualización atómica de saldos.
* [ ] Registro de transacciones.

### Fase 3 — Concurrencia

* [ ] Row locking.
* [ ] Prevención de race conditions.
* [ ] Orden determinista de locks.
* [ ] Manejo de deadlocks.
* [ ] Pruebas concurrentes.

### Fase 4 — Idempotencia

* [ ] Idempotency key.
* [ ] Prevención de transferencias duplicadas.
* [ ] Manejo de reintentos.

### Fase 5 — Outbox

* [ ] Modelo OutboxEvent.
* [ ] Creación atómica del evento.
* [ ] Worker.
* [ ] Reintentos.
* [ ] Manejo de errores.

### Fase 6 — Bancs Mock

* [ ] Mock de Bancs.
* [ ] Integración mediante worker.
* [ ] Simulación de errores.
* [ ] Reintentos.



---

# 15. Principio de desarrollo

El proyecto se desarrollará de manera incremental.

No se implementará toda la arquitectura de una sola vez.

Cada funcionalidad deberá:

1. Implementarse.
2. Revisarse.
3. Probarse.
4. Documentarse cuando corresponda.
5. Registrarse mediante un commit convencional.

El código debe mantenerse sencillo, entendible y consistente con el nivel de un desarrollador junior que conoce las tecnologías utilizadas.
