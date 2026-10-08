# Observability

Start after the application network exists:

```bash
docker compose -f observability/compose.yaml up -d
```

Codespaces ports: Grafana 3000, Prometheus 9090, cAdvisor 8088. Keep these forwarded ports private.

Grafana reads `GF_SECURITY_ADMIN_USER` and `GF_SECURITY_ADMIN_PASSWORD` from the root `.env` file. `.env.example` values are for local demos only; change them before exposing Grafana outside a private development environment. Do not include login screens, browser password managers or `.env` contents in submitted screenshots.

The provisioned dashboard is **LOGISTPULSE Operations Overview** with **HTTP Requests**, **p95 API latency** and **Container CPU** panels.
