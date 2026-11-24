# INC-2025-114: Webhook Retry Storm in Notification Hub

- **Incident ID**: INC-2025-114
- **Services**: notification-hub, billing-scheduler
- **Owning Team**: Commerce Backend
- **Lead Responder**: Devon Brooks

## Summary

Following the duplicate charge surge in `INC-2025-113`, `billing-scheduler` emitted double receipt events to `notification-hub`. A malformed webhook payload caused `notification-hub` workers to enter an immediate retry loop without exponential backoff.

## Resolution

`Devon Brooks` deployed jittered exponential backoff with a dead-letter queue for non-2xx webhook responses and capped per-tenant retry concurrency.
