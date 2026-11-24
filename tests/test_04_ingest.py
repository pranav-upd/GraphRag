"""Pytest Gate for Task 4: Batched UNWIND Cypher Ingestion."""

from __future__ import annotations

from neo4j import Driver

from graphrag.config import EMBEDDING_DIM, Settings
from graphrag.ingest import chunk_to_record, ingest_chunks
from graphrag.models import ChunkRecord, EntityMention
from graphrag.schema import setup_schema


def _sample_chunks() -> list[ChunkRecord]:
    return [
        ChunkRecord(
            chunk_id="inc_01::0",
            doc_id="inc_01",
            index=0,
            text="checkout-api timed out against orders-pg-primary.",
            embedding=[0.01] * EMBEDDING_DIM,
            entities=[
                EntityMention(name="checkout-api", label="service", score=0.95),
                EntityMention(name="orders-pg-primary", label="database", score=0.92),
            ],
        ),
        ChunkRecord(
            chunk_id="inc_02::0",
            doc_id="inc_02",
            index=0,
            text="Maya Lin found PgBouncer saturation on orders-pg-primary.",
            embedding=[0.02] * EMBEDDING_DIM,
            entities=[
                EntityMention(name="maya lin", label="person", score=0.96),
                EntityMention(name="orders-pg-primary", label="database", score=0.94),
            ],
        ),
        ChunkRecord(
            chunk_id="inc_03::0",
            doc_id="inc_03",
            index=0,
            text="Maya Lin rolled back ledger-service connection leak.",
            embedding=[0.03] * EMBEDDING_DIM,
            entities=[
                EntityMention(name="maya lin", label="person", score=0.97),
                EntityMention(name="ledger-service", label="service", score=0.91),
            ],
        ),
    ]


def test_chunk_to_record_payload_shape() -> None:
    chunk = _sample_chunks()[0]
    row = chunk_to_record(chunk)
    assert row["doc_id"] == "inc_01"
    assert row["chunk_id"] == "inc_01::0"
    assert row["text"] == chunk.text
    assert len(row["embedding"]) == EMBEDDING_DIM
    assert len(row["entities"]) == 2
    assert {e["name"] for e in row["entities"]} == {"checkout-api", "orders-pg-primary"}


def test_ingest_chunks_batched_and_idempotent(
    neo4j_driver: Driver,
    settings: Settings,
    clean_graph: None,
) -> None:
    setup_schema(neo4j_driver, database=settings.neo4j_database)
    chunks = _sample_chunks()

    # First run with batch_size=2 forces multiple UNWIND batches.
    count_1 = ingest_chunks(
        neo4j_driver,
        chunks,
        batch_size=2,
        database=settings.neo4j_database,
    )
    assert count_1 == len(chunks)

    def _counts() -> dict[str, int]:
        with neo4j_driver.session(database=settings.neo4j_database) as session:
            return {
                "docs": session.run("MATCH (d:Document) RETURN count(d) AS c").single()["c"],
                "chunks": session.run("MATCH (c:Chunk) RETURN count(c) AS c").single()["c"],
                "entities": session.run("MATCH (e:Entity) RETURN count(e) AS c").single()["c"],
                "has_chunk": session.run(
                    "MATCH ()-[r:HAS_CHUNK]->() RETURN count(r) AS c"
                ).single()["c"],
                "mentions": session.run(
                    "MATCH ()-[r:MENTIONS]->() RETURN count(r) AS c"
                ).single()["c"],
            }

    first = _counts()
    assert first == {
        "docs": 3,
        "chunks": 3,
        "entities": 4,  # checkout-api, orders-pg-primary, maya lin, ledger-service
        "has_chunk": 3,
        "mentions": 6,
    }

    # Double-run idempotency gate: counts must remain identical.
    count_2 = ingest_chunks(
        neo4j_driver,
        chunks,
        batch_size=2,
        database=settings.neo4j_database,
    )
    assert count_2 == len(chunks)
    assert _counts() == first
