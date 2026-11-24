# INC-2025-110: Fraud Engine P99 Latency Spike

- **Incident ID**: INC-2025-110
- **Service**: fraud-engine
- **Database**: ledger-cockroachdb
- **Owning Team**: Payments Reliability
- **Lead Responder**: Carlos Mendez

## Summary

Scoring requests in `fraud-engine` jumped from 45ms P99 to 1,420ms P99, causing payment authorization timeouts for high-value transactions.

## Investigation

`Carlos Mendez` correlated the tail latency directly with read queries against the `account_velocity` table in `ledger-cockroachdb`. Execution plans remained unchanged, indicating infrastructure rather than query regression.

## Escalation

`Payments Reliability` opened `INC-2025-111` to investigate leaseholder placement in `ledger-cockroachdb`.
