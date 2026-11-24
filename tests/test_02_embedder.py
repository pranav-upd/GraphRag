"""Pytest Gate for Task 2: Deterministic Chunking & Local Embeddings."""

from __future__ import annotations

import math

import pytest

from graphrag.config import EMBEDDING_DIM
from graphrag.embedder import LocalEmbedder, chunk_markdown, make_chunk_id


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)


def test_make_chunk_id_is_deterministic_and_sensitive() -> None:
    id_a = make_chunk_id("inc_01", 0, "checkout-api 504 timeout")
    id_b = make_chunk_id("inc_01", 0, "checkout-api 504 timeout")
    assert isinstance(id_a, str) and len(id_a) >= 12
    assert id_a == id_b

    assert id_a != make_chunk_id("inc_02", 0, "checkout-api 504 timeout")
    assert id_a != make_chunk_id("inc_01", 1, "checkout-api 504 timeout")
    assert id_a != make_chunk_id("inc_01", 0, "different chunk text")


def test_chunk_markdown_reproducible_and_bounded() -> None:
    sample_md = (
        "# INC-2025-101\n\n"
        + ("checkout-api experienced 504 timeouts waiting on orders-pg-primary. " * 12)
        + "\n\n## Resolution\n\n"
        + ("Traffic shifted to eu-west-1 while Maya Lin inspected PgBouncer. " * 10)
    )
    chunks_first = chunk_markdown("inc_01", sample_md, chunk_size=250, chunk_overlap=40)
    chunks_second = chunk_markdown("inc_01", sample_md, chunk_size=250, chunk_overlap=40)

    assert len(chunks_first) >= 2
    assert [c.chunk_id for c in chunks_first] == [c.chunk_id for c in chunks_second]
    assert [c.index for c in chunks_first] == list(range(len(chunks_first)))
    assert all(c.doc_id == "inc_01" and c.text.strip() for c in chunks_first)


def test_chunk_markdown_validates_arguments() -> None:
    with pytest.raises(ValueError):
        chunk_markdown("doc", "hello world", chunk_size=0, chunk_overlap=0)
    with pytest.raises(ValueError):
        chunk_markdown("doc", "hello world", chunk_size=100, chunk_overlap=100)
    with pytest.raises(ValueError):
        chunk_markdown("doc", "hello world", chunk_size=100, chunk_overlap=-1)


def test_local_embedder_384_dim_and_semantics() -> None:
    embedder = LocalEmbedder()
    vectors = embedder.embed_texts(
        [
            "checkout-api returned HTTP 504 gateway timeout errors",
            "payment checkout gateway timed out with 504 status",
            "classic sourdough bread fermentation recipe with flour and water",
        ]
    )

    assert len(vectors) == 3
    for vec in vectors:
        assert isinstance(vec, list)
        assert len(vec) == EMBEDDING_DIM
        assert all(isinstance(v, float) for v in vec)

    sim_related = _cosine_similarity(vectors[0], vectors[1])
    sim_unrelated = _cosine_similarity(vectors[0], vectors[2])
    assert sim_related > sim_unrelated + 0.15


def test_embed_chunks_populates_embeddings() -> None:
    embedder = LocalEmbedder()
    chunks = chunk_markdown("inc_test", "# Title\n\nPgBouncer pool exhausted on orders-pg-primary.")
    embedded = embedder.embed_chunks(chunks)

    assert len(embedded) == len(chunks)
    assert all(len(c.embedding) == EMBEDDING_DIM for c in embedded)
