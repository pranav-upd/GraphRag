# INC-2025-102: PgBouncer Pool Exhaustion on Orders Primary

- **Incident ID**: INC-2025-102
- **Database**: orders-pg-primary
- **Technology**: PgBouncer
- **Owning Team**: Data Infra
- **Lead Responder**: Maya Lin

## Summary

Connection pool utilization on `orders-pg-primary` reached 100% saturation for 36 minutes, causing client queueing delays across dependent services. `PgBouncer` reported 4,200 waiting client connections with zero idle server slots.

## Root Cause Analysis

`Maya Lin` inspected `pg_stat_activity` and identified hundreds of long-lived `idle in transaction` sessions originating from a newly deployed worker pool rather than `checkout-api` itself. Those leaked transactions held connections open until the 15-minute server timeout fired.

## Follow-Up

The offending transaction leak was traced to deployment `CHG-8842` documented in `INC-2025-103`.
