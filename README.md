# LOGISTPULSE-GOLDEN V1.0

**Independent LOGISTdragon universe — Operations, Logistics, IoT and Platform Engineering laboratory.**

LOGISTPULSE simulates a national restaurant/retail operation with 300 stores, distribution centers, fleet telemetry, kitchen equipment and event-driven order fulfillment. It is intentionally independent from BANKdragon/BANKPULSE.

## Product domains

- **Smart Inventory** — stock, forecast and stockout risk.
- **Supply & Distribution** — trucks, ETA and cold chain.
- **Smart Operations** — MQTT equipment telemetry and operational state.
- **Order Fulfillment** — event-driven kitchen queue using Kafka-compatible Redpanda.

## Architecture

```text
Browser / Operations Console :8080
          |
       Nginx Edge
          |
  +-------+---------+-----------+
  |       |         |           |
Inventory Distribution Operations Fulfillment
  |       |         |           |
Postgres Postgres  MongoDB    Postgres
                    ^           |
                    |           v
                  MQTT       Redpanda
                    ^           |
              Telemetry      Worker
              Simulator

Prometheus + Grafana + cAdvisor observe the runtime.
```

## Prerequisites

- Docker Engine or Docker Desktop with Docker Compose v2.
- Git and `curl`.
- Python 3 for the order smoke test, which uses only the standard library.
- At least 6 GB of available memory for the full stack; Redpanda and MongoDB are the largest services.

## Run locally

```bash
cp .env.example .env
docker compose up -d --build
docker compose ps
bash scripts/smoke.sh
bash scripts/smoke-orders.sh
```

Open `http://localhost:8080` or forward port **8080** in Codespaces. The console views are **Control Center**, **Inventario**, **Distribución**, **Smart Operations**, **Fulfillment** and **Platform**.

The edge forwards `/api/inventory/`, `/api/distribution/`, `/api/operations/` and `/api/fulfillment/` to their matching APIs. Fulfillment accepts `POST /api/fulfillment/orders` and lists the latest 20 orders at `GET /api/fulfillment/orders`. A successful create returns HTTP 201 with `WAITING`; the PostgreSQL outbox retries publishing `ORDER_CREATED` until Redpanda accepts it, and the kitchen worker advances the order to `READY`.

## Tests

`scripts/smoke.sh` checks console and service health through Nginx. `scripts/smoke-orders.sh` creates a unique order and waits for it to reach `READY`; its optional arguments are the base URL and maximum wait in seconds:

```bash
bash scripts/smoke-orders.sh http://localhost:8080 90
```

Both are required local checks and run in the pull-request integration workflow. For a clean rebuild, run `docker compose down -v` before starting again; this deletes local database volumes and their data.

## Observability

```bash
docker compose -f observability/compose.yaml up -d
```

- Grafana `3000` — credentials come from `.env` (`GF_SECURITY_ADMIN_USER` and `GF_SECURITY_ADMIN_PASSWORD`). The example file contains demo-only values; replace them before sharing a remotely accessible environment.
- Prometheus `9090`
- cAdvisor `8088`

Grafana provisions the dashboard **LOGISTPULSE Operations Overview** with **HTTP Requests**, **p95 API latency** and **Container CPU** panels. Close it with `docker compose -f observability/compose.yaml down`.

## Troubleshooting

- **An API remains unhealthy:** run `docker compose ps -a` and `docker compose logs --tail=100 postgres inventory-api logistics-api operations-api fulfillment-api`; wait for PostgreSQL initialization and check that `.env` matches `.env.example` keys.
- **The console opens but an API call fails:** run `bash scripts/smoke.sh` and inspect `docker compose logs --tail=100 console <service>`.
- **An order stays in `WAITING`:** inspect `docker compose logs --tail=150 fulfillment-api fulfillment-worker redpanda`, then confirm `docker compose ps` reports Redpanda running. The outbox retains unpublished events and retries while the worker is running.
- **Grafana does not start:** confirm the application network exists (`docker network inspect logistpulse-net`) and inspect `docker compose -f observability/compose.yaml logs --tail=100 grafana prometheus cadvisor`.
- **A host port is busy:** stop the process using 8080, 3000, 8088 or 9090, or change the host-side port mapping in the corresponding Compose file.

Use `docker compose down` to stop the application. This preserves database volumes; `docker compose down -v` permanently removes them.

## Git/CI model

Work through feature branches and Pull Requests; do not make delivery commits directly on `main`. For example:

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/short-description
# make and test changes
git add <files>
git commit -m "Describe the change"
git push -u origin feature/short-description
```

Open a PR from that branch to `main`, wait for review and all CI checks, then merge it in GitHub. `.github/workflows/ci.yml` validates the architecture contract and Compose files, builds the stack, runs both smoke tests and validates Prometheus/Grafana. Only claim a PR, review, checks or merge after the corresponding GitHub result is available.

## Academic ownership

Design of Systems teams own frontend/backend product evolution. Software Development teams act as DevOps/Platform teams: Codespaces, CI/CD, containerization, integration readiness, observability and later DevSecOps security gates.

See `docs/` for architecture, data ownership, the acceptance plan and incident runbooks. Never commit `.env`, screenshots containing credentials, or raw secrets; `.env` is excluded by `.gitignore`.

