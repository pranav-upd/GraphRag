# INC-2025-108: Kafka Broker Disk I/O Saturation

- **Incident ID**: INC-2025-108
- **Database**: events-kafka-us-east
- **Region**: us-east-1
- **Owning Team**: Data Infra
- **Lead Responder**: Priya Nair

## Summary

Brokers 3 and 4 of `events-kafka-us-east` in `us-east-1` experienced 99% NVMe disk utilization and elevated fsync latencies above 450ms.

## Root Cause

`Priya Nair` traced the abnormal write throughput (1.8 GB/s vs. 220 MB/s baseline) to a full-catalog backfill job publishing raw document payloads onto the `catalog.mutations` topic.

## Resolution

`Data Infra` throttled producer quotas for the backfill client and coordinated with the search team under `INC-2025-109`.
