# INC-2025-113: Duplicate Subscription Charges from Billing Scheduler

- **Incident ID**: INC-2025-113
- **Services**: billing-scheduler, ledger-service
- **Owning Team**: Payments Reliability
- **Lead Responder**: Carlos Mendez

## Summary

412 recurring subscribers were billed twice during the 00:00 UTC renewal window when `billing-scheduler` retried timed-out HTTP calls to `ledger-service` without propagating an idempotency key header.

## Remediation

`Carlos Mendez` issued automated refunds via `ledger-service`, enforced mandatory `Idempotency-Key` headers on all charge endpoints, and audited downstream webhook notifications in `INC-2025-114`.
