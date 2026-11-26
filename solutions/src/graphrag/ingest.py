"""Task 4 Solution: Batched UNWIND Cypher Ingestion."""

from __future__ import annotations

from typing import Any

from neo4j import Driver

from graphrag.models import ChunkRecord

BATCH_INGEST_CYPHER = """
UNWIND $records AS row
MERGE (d:Document {id: row.doc_id})
MERGE (c:Chunk {id: row.chunk_id})
SET c.text = row.text,
    c.index = row.index,
    c.embedding = row.embedding
MERGE (d)-[:HAS_CHUNK]->(c)
FOREACH (ent IN row.entities |
    MERGE (e:Entity {name: ent.name})
    SET e.label = coalesce(e.label, ent.label)
    MERGE (c)-[:MENTIONS]->(e)
)
""".strip()


def chunk_to_record(chunk: ChunkRecord) -> dict[str, Any]:
    """Serialize a `ChunkRecord` into a Cypher parameter dictionary."""
    return {
        "doc_id": chunk.doc_id,
        "chunk_id": chunk.chunk_id,
        "text": chunk.text,
        "index": chunk.index,
        "embedding": [float(v) for v in chunk.embedding],
        "entities": [
            {
                "name": ent.name,
                "label": ent.label,
                "score": float(ent.score),
            }
            for ent in chunk.entities
        ],
    }


def ingest_chunks(
    driver: Driver,
    chunks: list[ChunkRecord],
    batch_size: int = 50,
    database: str | None = None,
) -> int:
    """Ingest `ChunkRecord`s into Neo4j using batched UNWIND Cypher transactions."""
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")
    if not chunks:
        return 0

    total = 0
    with driver.session(database=database) as session:
        for start in range(0, len(chunks), batch_size):
            batch = [chunk_to_record(c) for c in chunks[start : start + batch_size]]
            session.execute_write(
                lambda tx, rows=batch: tx.run(BATCH_INGEST_CYPHER, records=rows).consume()
            )
            total += len(batch)

    return total
