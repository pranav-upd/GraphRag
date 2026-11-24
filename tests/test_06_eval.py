"""Pytest Gate for Task 6: Cross-Encoder Reranking & Local Benchmark Evaluation."""

from __future__ import annotations

import pytest

from graphrag.config import EVAL_QUERIES_PATH
from graphrag.eval import evaluate_strategy, load_eval_cases, recall_at_k
from graphrag.models import EvalCase, RetrievedChunk
from graphrag.reranker import CrossEncoderReranker


def test_load_eval_cases() -> None:
    cases = load_eval_cases(EVAL_QUERIES_PATH)
    assert len(cases) >= 5
    for case in cases:
        assert isinstance(case, EvalCase)
        assert case.query.strip()
        assert len(case.relevant_doc_ids) >= 2


def test_recall_at_k_deduplicates_and_handles_edge_cases() -> None:
    # Duplicate doc_ids in top ranks should only count once toward top-k unique docs
    assert recall_at_k(["d1", "d1", "d2", "d3"], ["d1", "d3"], k=3) == pytest.approx(1.0)
    assert recall_at_k(["d1", "d2", "d4"], ["d1", "d3"], k=3) == pytest.approx(0.5)
    assert recall_at_k(["d4", "d5"], ["d1", "d2"], k=3) == pytest.approx(0.0)
    assert recall_at_k(["d1"], [], k=3) == pytest.approx(0.0)


def test_cross_encoder_reranker_promotes_most_relevant_chunk() -> None:
    reranker = CrossEncoderReranker()
    query = "Which deployment caused the ledger-service database connection leak?"
    candidates = [
        RetrievedChunk(
            chunk_id="c_noise",
            doc_id="inc_15",
            text="An intermediate mTLS certificate on Envoy sidecars in eu-west-1 expired.",
            score=0.95,
            source="vector",
        ),
        RetrievedChunk(
            chunk_id="c_target",
            doc_id="inc_03",
            text="Deployment CHG-8842 introduced an unclosed async database session in ledger-service.",
            score=0.40,
            source="graph_hop",
        ),
        RetrievedChunk(
            chunk_id="c_other",
            doc_id="inc_09",
            text="search-indexer emitted 14 million mutation events to catalog-opensearch.",
            score=0.70,
            source="graph_hop",
        ),
    ]

    reranked = reranker.rerank(query, candidates, top_k=2)
    assert len(reranked) == 2
    assert reranked[0].chunk_id == "c_target"
    assert reranked[0].source == "reranked"
    assert reranked[0].score >= reranked[1].score


def test_evaluate_strategy_returns_benchmark_result() -> None:
    cases = [
        EvalCase(query_id="q1", query="first query", relevant_doc_ids=["d1", "d2"]),
        EvalCase(query_id="q2", query="second query", relevant_doc_ids=["d3", "d4"]),
    ]

    def _fake_retrieve(query: str) -> list[RetrievedChunk]:
        if "first" in query:
            return [
                RetrievedChunk("c1", "d1", "text", 0.9),
                RetrievedChunk("c2", "d2", "text", 0.8),
            ]
        return [
            RetrievedChunk("c3", "d3", "text", 0.9),
            RetrievedChunk("c4", "d9", "text", 0.7),
        ]

    res = evaluate_strategy("Mock Strategy", cases, _fake_retrieve, k=3)
    assert res.strategy == "Mock Strategy"
    assert res.num_queries == 2
    assert res.recall_at_3 == pytest.approx(0.75)
    assert res.avg_latency_ms >= 0.0
