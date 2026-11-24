# INC-2025-103: Connection Leak in Ledger Sync Deployment

- **Incident ID**: INC-2025-103
- **Services**: ledger-service, billing-scheduler
- **Owning Team**: Payments Reliability
- **Lead Responder**: Maya Lin

## Summary

Deployment `CHG-8842` introduced an unclosed async database session inside `ledger-service` whenever `billing-scheduler` triggered a reconciliation batch. Each failed retry left an open transaction pinned against `orders-pg-primary`.

## Remediation

`Maya Lin` rolled back `CHG-8842` and added a strict `async with` context manager guard plus a 30-second `idle_in_transaction_session_timeout` policy. Connection pool utilization dropped back below 18% within four minutes of rollback.
