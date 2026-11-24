# INC-2025-107: Inventory Worker Kafka Consumer Lag

- **Incident ID**: INC-2025-107
- **Service**: inventory-worker
- **Database**: events-kafka-us-east
- **Technology**: Apache Kafka
- **Owning Team**: Commerce Backend

## Summary

Stock reservation updates processed by `inventory-worker` fell 480,000 messages behind on `events-kafka-us-east`. Storefront product pages displayed stale availability counts for 52 minutes.

## Observations

Consumer group rebalancing occurred every 90 seconds because broker fetch responses intermittently timed out. `inventory-worker` memory and CPU metrics remained healthy throughout the incident.

## Escalation

`Commerce Backend` paged `Data Infra` to inspect broker health on `events-kafka-us-east` (`INC-2025-108`).
