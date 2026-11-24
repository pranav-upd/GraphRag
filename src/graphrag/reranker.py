"""Task 6 (Part A): Cross-Encoder Reranking.

Pytest gate: tests/test_06_eval.py

Requirements:
1. Load a local Sentence Transformers `CrossEncoder` model on CPU.
2. Score `(query, candidate.text)` pairs for all retrieved candidates.
3. Return the top `top_k` `RetrievedChunk` items sorted in descending order of
   Cross-Encoder score, with `source="reranked"` and updated `.score`.
"""

from __future__ import annotations

from graphrag.models import RetrievedChunk

DEFAULT_CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class CrossEncoderReranker:
    """Local Cross-Encoder reranker for precision ordering of retrieved chunks."""

    def __init__(
        self,
        model_name: str = DEFAULT_CROSS_ENCODER_MODEL,
        device: str = "cpu",
    ) -> None:
        self.model_name = model_name
        self.device = device
        raise NotImplementedError("Task 6: Initialize the local CrossEncoder model.")

    def rerank(
        self,
        query: str,
        candidates: list[RetrievedChunk],
        top_k: int = 3,
    ) -> list[RetrievedChunk]:
        """Rescore candidate chunks with the Cross-Encoder and return top-k results."""
        raise NotImplementedError("Task 6: Implement Cross-Encoder reranking.")
