# Acceptance test plan

A fresh Codespace is considered GOLDEN-ready only if:

1. `docker --version` and `docker compose version` succeed.
2. `docker compose config --services` returns all domain and infrastructure services.
3. `docker compose up -d --build` completes without Recovery Mode.
4. `docker compose ps` shows databases and domain APIs healthy.
5. `bash scripts/smoke.sh` reports the console and four API health routes reachable through Nginx.
6. `bash scripts/smoke-orders.sh` creates an order through the edge and observes its transition to `READY`.
7. Port 8080 displays the interactive Operations Command Center; its views are Control Center, Inventario, Distribución, Smart Operations, Fulfillment and Platform.
8. `docker compose -f observability/compose.yaml up -d` starts Grafana, Prometheus and cAdvisor.
9. Grafana on 3000 provisions **LOGISTPULSE Operations Overview** with HTTP Requests, p95 API latency and Container CPU panels.
10. A Pull Request triggers `.github/workflows/ci.yml`; both jobs pass and the integration job runs both smoke tests.

## Evidence to retain for delivery

- Capture `docker compose ps` with healthy application APIs and running infrastructure containers.
- Capture the terminal output from both smoke scripts, including the order ID reaching `READY`.
- Capture the dashboard with its three panel titles and useful data visible.
- Store evidence in the course submission location, not in the source tree unless requested. Keep `.env`, browser autofill, passwords and tokens out of screenshots; redact them before sharing.
