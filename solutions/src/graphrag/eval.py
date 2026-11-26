"""Task 6 Solution (Part B): Multi-Hop Recall@k & Local Benchmark Evaluation."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable

from graphrag.models import BenchmarkResult, EvalCase, RetrievedChunk


def load_eval_cases(path: Path | str) -> list[EvalCase]:
    """Load multi-hop evaluation queries from a JSON file."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [
        EvalCase(
            query_id=item["query_id"],
            query=item["query"],
            relevant_doc_ids=list(item["relevant_doc_ids"]),
            hops=int(item.get("hops", 2)),
        )
        for item in raw
    ]


def recall_at_k(
    retrieved_doc_ids: list[str],
    relevant_doc_ids: list[str],
    k: int = 3,
) -> float:
    """Compute Recall@k over unique retrieved document IDs in rank order."""
    if not relevant_doc_ids or k <= 0:
        return 0.0

    seen: set[str] = set()
    top_unique: list[str] = []
    for doc_id in retrieved_doc_ids:
        if doc_id not in seen:
            seen.add(doc_id)
            top_unique.append(doc_id)
            if len(top_unique) == k:
                break

    relevant_set = set(relevant_doc_ids)
    hits = len(set(top_unique) & relevant_set)
    return hits / len(relevant_set)


def evaluate_strategy(
    name: str,
    cases: list[EvalCase],
    retrieve_fn: Callable[[str], list[RetrievedChunk]],
    k: int = 3,
) -> BenchmarkResult:
    """Benchmark a retrieval strategy for mean Recall@k and average latency (ms)."""
    if not cases:
        return BenchmarkResult(
            strategy=name,
            recall_at_3=0.0,
            avg_latency_ms=0.0,
            num_queries=0,
        )

    recalls: list[float] = []
    latencies_ms: list[float] = []

    for case in cases:
        t0 = time.perf_counter()
        results = retrieve_fn(case.query)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        doc_ids = [r.doc_id for r in results]
        recalls.append(recall_at_k(doc_ids, case.relevant_doc_ids, k=k))
        latencies_ms.append(elapsed_ms)

    return BenchmarkResult(
        strategy=name,
        recall_at_3=sum(recalls) / len(recalls),
        avg_latency_ms=sum(latencies_ms) / len(latencies_ms),
        num_queries=len(cases),
    )
