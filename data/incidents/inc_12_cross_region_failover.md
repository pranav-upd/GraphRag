# INC-2025-112: Cross-Region Failover Drift in ap-south-1

- **Incident ID**: INC-2025-112
- **Service**: checkout-api
- **Region**: ap-south-1
- **Owning Team**: Core Platform
- **Lead Responder**: Hannah Sato

## Summary

During regional failover testing in `ap-south-1`, `checkout-api` continued routing fraud checks to `us-east-1` endpoints because DNS weighted records had a stale 600-second TTL.

## Mitigation

`Hannah Sato` lowered health-check failover TTLs to 30 seconds and added automated regional affinity assertions in `Core Platform` deployment pipelines.
