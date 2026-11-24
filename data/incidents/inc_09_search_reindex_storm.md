# INC-2025-109: Search Indexer Unthrottled Reindex Storm

- **Incident ID**: INC-2025-109
- **Service**: search-indexer
- **Database**: catalog-opensearch
- **Owning Team**: Commerce Backend
- **Lead Responder**: Priya Nair

## Summary

A scheduled mapping migration for `catalog-opensearch` triggered an unthrottled full-catalog reindex job in `search-indexer`. The job emitted 14 million oversized mutation events to `events-kafka-us-east` in under 20 minutes.

## Remediation

`Priya Nair` paused the backfill worker, enabled gzip compression on `search-indexer` producers, and capped batch emission at 5,000 events per second.
