# C4 Container View

```text
Operator Browser
      |
      v
Nginx Edge / Interactive Console :8080
      |
      +--> Inventory API ------> PostgreSQL inventory_db
      +--> Distribution API ---> PostgreSQL logistics_db
      +--> Operations API -----> MongoDB operations
      |          ^
      |          |
      |        MQTT <--- Telemetry Simulator
      +--> Fulfillment API ----> PostgreSQL fulfillment_db
                 |                         |
                 |                  Transactional outbox
                 |                         |
                 +--------------------> Fulfillment Worker
                                            |
                                         Redpanda

The fulfillment worker publishes pending outbox records to Redpanda and consumes the resulting order events before advancing their status.

All APIs ---> Prometheus ---> Grafana
Docker ----> cAdvisor ------> Prometheus
```
