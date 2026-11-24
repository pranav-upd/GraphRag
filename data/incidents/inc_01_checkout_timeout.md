# INC-2025-101: Checkout API 504 Timeout Surge

- **Incident ID**: INC-2025-101
- **Service**: checkout-api
- **Region**: us-east-1
- **Owning Team**: Commerce Backend
- **Lead Responder**: Hannah Sato

## Summary

Between 14:12 UTC and 14:48 UTC, `checkout-api` experienced a 34% spike in HTTP 504 gateway timeouts in `us-east-1`. Customers attempting to finalize cart orders saw spinner hangs lasting 30 seconds before request termination.

## Observations

Application traces showed worker threads blocked waiting for database connections from `orders-pg-primary`. CPU utilization on `checkout-api` pods remained below 25%, ruling out compute saturation. Upstream traffic volume was normal for a Tuesday afternoon.

## Resolution

Traffic was partially shifted to `eu-west-1` while the database connection bottleneck on `orders-pg-primary` was investigated under `INC-2025-102`.
