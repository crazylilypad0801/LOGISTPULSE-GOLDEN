# API layers

The domain APIs keep HTTP controllers separate from persistence and external integration code. `app.py` composes the FastAPI application, request metrics and health endpoint; each `routes.py` declares the REST contract and delegates reads or mutations to `repository.py`.

| API | Controller | Persistence/model | Integration |
|---|---|---|---|
| Inventory | `services/inventory-api/routes.py` | `services/inventory-api/repository.py` (PostgreSQL) | — |
| Distribution | `services/logistics-api/routes.py` | `services/logistics-api/repository.py` (PostgreSQL) | — |
| Operations | `services/operations-api/routes.py` | `services/operations-api/repository.py` (MongoDB) | `services/operations-api/telemetry.py` (MQTT) |
| Fulfillment | `services/fulfillment-api/routes.py` | `services/fulfillment-api/repository.py` (PostgreSQL orders and outbox) | `services/fulfillment-worker/app.py` (Redpanda producer/consumer) |

This is a service/repository MVC separation suited to FastAPI rather than a framework-provided ORM model layer. The REST controllers remain the only HTTP boundary; SQL, MongoDB operations and MQTT ingestion are outside those handlers.