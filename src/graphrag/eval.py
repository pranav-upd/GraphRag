"""Task 6 (Part B): Multi-Hop Recall@k & Local Benchmark Evaluation.

Pytest gate: tests/test_06_eval.py

Requirements:
1. `load_eval_cases`: Load evaluation cases from `data/eval_queries.json`.
2. `recall_at_k`: Compute Recall@k over unique retrieved document IDs in rank order
   compared against `relevant_doc_ids`.
3. `evaluate_strategy`: Run a retrieval callable over all `EvalCase`s, measure
   wall-clock latency per query in milliseconds, and return a `BenchmarkResult`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from graphrag.models import BenchmarkResult, EvalCase, RetrievedChunk


def load_eval_cases(path: Path | str) -> list[EvalCase]:
    """Load multi-hop evaluation queries from a JSON file."""
    raise NotImplementedError("Task 6: Load EvalCase records from JSON.")


def recall_at_k(
    retrieved_doc_ids: list[str],
    relevant_doc_ids: list[str],
    k: int = 3,
) -> float:
    """Compute Recall@k for a single query.

    Deduplicate `retrieved_doc_ids` while preserving rank order, take the top `k`
    unique document IDs, and return `|top_k ∩ relevant| / |relevant|`.
    Return `0.0` if `relevant_doc_ids` is empty.
    """
    raise NotImplementedError("Task 6: Implement Recall@k metric.")


def evaluate_strategy(
    name: str,
    cases: list[EvalCase],
    retrieve_fn: Callable[[str], list[RetrievedChunk]],
    k: int = 3,
) -> BenchmarkResult:
    """Benchmark a retrieval strategy for mean Recall@k and average latency (ms)."""
    raise NotImplementedError("Task 6: Implement strategy evaluation loop.")
