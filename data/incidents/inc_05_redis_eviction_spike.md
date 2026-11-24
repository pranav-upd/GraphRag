# INC-2025-105: Session Redis Cluster Memory Eviction Spike

- **Incident ID**: INC-2025-105
- **Database**: session-redis-cluster
- **Technology**: Redis
- **Owning Team**: Identity SRE
- **Lead Responder**: Devon Brooks

## Summary

`session-redis-cluster` hit its `maxmemory` ceiling of 64 GB in `eu-west-1`, triggering aggressive `allkeys-lru` evictions that purged active user session tokens.

## Investigation

`Devon Brooks` ran `redis-cli --bigkeys` and discovered 41 GB of unexpected `notif:dedup:*` keys stored without expiration timestamps. Normally, `session-redis-cluster` only holds short-lived OAuth session payloads.

## Mitigation

`Devon Brooks` purged the expired notification deduplication namespace and coordinated the configuration fix in `INC-2025-106`.
