"""Pytest Gate for Task 5: Hybrid Vector + 2-Hop Cypher Search."""

from __future__ import annotations

import time

from neo4j import Driver

from graphrag.config import EMBEDDING_DIM, Settings
from graphrag.ingest import ingest_chunks
from graphrag.models import ChunkRecord, EntityMention
from graphrag.retriever import GraphRetriever
from graphrag.schema import setup_schema


class _StubEmbedder:
    """Deterministic unit-vector embedder for controlled multi-hop retrieval tests."""

    def __init__(self, mapping: dict[str, list[float]]) -> None:
        self._mapping = mapping

    def embed_query(self, query: str) -> list[float]:
        return self._mapping[query]


def _basis_vector(axis: int) -> list[float]:
    vec = [0.0] * EMBEDDING_DIM
    vec[axis] = 1.0
    return vec


def test_vector_and_hybrid_two_hop_with_fan_out_cap(
    neo4j_driver: Driver,
    settings: Settings,
    clean_graph: None,
) -> None:
    setup_schema(neo4j_driver, database=settings.neo4j_database)

    # Chain: seed_doc (axis 0) --[orders-pg-primary]--> hop1_doc (axis 1) --[maya lin]--> hop2_doc (axis 2)
    # Hub: "us-east-1" connected to seed_doc + 6 distractor docs (degree 7)
    chunks = [
        ChunkRecord(
            chunk_id="seed::0",
            doc_id="seed_doc",
            index=0,
            text="checkout-api experienced 504 timeouts against orders-pg-primary in us-east-1.",
            embedding=_basis_vector(0),
            entities=[
                EntityMention(name="orders-pg-primary", label="database"),
                EntityMention(name="us-east-1", label="region"),
            ],
        ),
        ChunkRecord(
            chunk_id="hop1::0",
            doc_id="hop1_doc",
            index=0,
            text="Maya Lin traced PgBouncer exhaustion on orders-pg-primary.",
            embedding=_basis_vector(1),
            entities=[
                EntityMention(name="orders-pg-primary", label="database"),
                EntityMention(name="maya lin", label="person"),
            ],
        ),
        ChunkRecord(
            chunk_id="hop2::0",
            doc_id="hop2_doc",
            index=0,
            text="Maya Lin rolled back deployment CHG-8842 in ledger-service.",
            embedding=_basis_vector(2),
            entities=[
                EntityMention(name="maya lin", label="person"),
                EntityMention(name="ledger-service", label="service"),
            ],
        ),
    ]

    # Add 6 distractor chunks attached only to the high-degree hub entity "us-east-1"
    for i in range(6):
        chunks.append(
            ChunkRecord(
                chunk_id=f"hub_{i}::0",
                doc_id=f"hub_doc_{i}",
                index=0,
                text=f"Unrelated maintenance notice #{i} in us-east-1.",
                embedding=_basis_vector(10 + i),
                entities=[EntityMention(name="us-east-1", label="region")],
            )
        )

    ingest_chunks(neo4j_driver, chunks, batch_size=20, database=settings.neo4j_database)
    # Brief pause to ensure Neo4j vector index has indexed newly inserted Chunk nodes
    time.sleep(1.0)

    embedder = _StubEmbedder({"checkout timeout": _basis_vector(0)})
    retriever = GraphRetriever(
        driver=neo4j_driver,
        embedder=embedder,  # type: ignore[arg-type]
        database=settings.neo4j_database,
    )

    # 1. Baseline flat vector search finds seed_doc at rank 1
    vec_results = retriever.vector_search("checkout timeout", top_k=1)
    assert len(vec_results) == 1
    assert vec_results[0].doc_id == "seed_doc"

    # 2. Hybrid search with max_entity_degree=4 traverses orders-pg-primary -> maya lin
    #    while capping out the high-degree hub "us-east-1" (degree 7).
    hybrid_results = retriever.hybrid_search(
        "checkout timeout",
        seed_k=1,
        max_entity_degree=4,
        max_neighbors_per_entity=5,
        limit=10,
    )
    doc_ids = {r.doc_id for r in hybrid_results}
    assert "seed_doc" in doc_ids
    assert "hop1_doc" in doc_ids, "Expected 1-hop entity neighbor (orders-pg-primary)."
    assert "hop2_doc" in doc_ids, "Expected 2-hop entity neighbor (via maya lin)."
    assert not any(d.startswith("hub_doc_") for d in doc_ids), (
        f"High-degree hub distractors should be filtered by max_entity_degree=4, got {doc_ids}"
    )
