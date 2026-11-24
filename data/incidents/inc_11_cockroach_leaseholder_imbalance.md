# INC-2025-111: CockroachDB Leaseholder Imbalance in ap-south-1

- **Incident ID**: INC-2025-111
- **Database**: ledger-cockroachdb
- **Technology**: CockroachDB
- **Region**: ap-south-1
- **Owning Team**: Data Infra

## Summary

After a routine node drain in `ap-south-1`, 78% of `ledger-cockroachdb` range leaseholders migrated to two nodes in `us-east-1`, adding 180ms cross-region round-trip latency to every strongly consistent read from `fraud-engine`.

## Resolution

`Data Infra` rebalanced survival goals and pinned regional-by-row lease preferences for `ap-south-1`. Related cross-region routing behavior was reviewed in `INC-2025-112`.
