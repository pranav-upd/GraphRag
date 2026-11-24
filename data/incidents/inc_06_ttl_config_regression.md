# INC-2025-106: Missing TTL Regression in Notification Hub

- **Incident ID**: INC-2025-106
- **Services**: notification-hub, feature-flag-service
- **Owning Team**: Core Platform
- **Lead Responder**: Devon Brooks

## Summary

A configuration change rolled out via `feature-flag-service` set the deduplication cache TTL in `notification-hub` to `0`, which the client library interpreted as no expiration instead of bypassing cache writes.

## Impact

Because `notification-hub` shared `session-redis-cluster` for transient deduplication keys, unbounded key growth filled cluster memory over 18 hours and triggered authentication evictions.

## Action Items

`Core Platform` isolated `notification-hub` onto a dedicated Redis instance and added schema validation in `feature-flag-service` to reject zero-TTL values.
