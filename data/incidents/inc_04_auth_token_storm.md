# INC-2025-104: Auth Gateway Token Verification Storm

- **Incident ID**: INC-2025-104
- **Service**: auth-gateway
- **Database**: session-redis-cluster
- **Region**: eu-west-1
- **Owning Team**: Identity SRE

## Summary

At 08:05 UTC, `auth-gateway` in `eu-west-1` began rejecting 19% of valid bearer tokens with HTTP 401 errors. Mobile and web clients automatically retried token refresh calls, amplifying request volume by 5x.

## Observations

Cache miss rates on `session-redis-cluster` jumped from 0.4% to 62% within two minutes. Latency on downstream identity database reads climbed from 4ms to 190ms due to the sudden cache stampede.

## Next Steps

`Identity SRE` escalated the cache eviction anomaly on `session-redis-cluster` under `INC-2025-105`.
