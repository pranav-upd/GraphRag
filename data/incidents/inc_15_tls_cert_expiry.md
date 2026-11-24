# INC-2025-115: Internal mTLS Certificate Expiry in eu-west-1

- **Incident ID**: INC-2025-115
- **Service**: auth-gateway
- **Technology**: Envoy
- **Region**: eu-west-1
- **Owning Team**: Core Platform
- **Lead Responder**: Hannah Sato

## Summary

An intermediate mTLS certificate on `Envoy` sidecars in `eu-west-1` expired at 03:00 UTC, breaking service-to-service handshakes between `checkout-api` and `auth-gateway` for 14 minutes.

## Remediation

`Hannah Sato` rotated the certificate chain via the automated PKI issuer and added a 14-day pre-expiry PagerDuty alert owned by `Core Platform` and `Identity SRE`.
