"""Task 1: Neo4j Constraints & Vector Index.

Pytest gate: tests/test_01_schema.py

Graph schema to enforce:
    (:Document {id})-[:HAS_CHUNK]->(:Chunk {id, text, embedding})-[:MENTIONS]->(:Entity {name})

Requirements:
1. Create uniqueness constraints (with IF NOT EXISTS) on:
   - Document.id
   - Chunk.id
   - Entity.name
2. Create a 384-dimensional cosine similarity vector index (with IF NOT EXISTS)
   named `VECTOR_INDEX_NAME` on `:Chunk(embedding)`.
3. Ensure `setup_schema` is fully idempotent and safe to execute repeatedly.
"""

from __future__ import annotations

from neo4j import Driver

from graphrag.config import EMBEDDING_DIM, SIMILARITY_FUNCTION, VECTOR_INDEX_NAME

__all__ = [
    "EMBEDDING_DIM",
    "SIMILARITY_FUNCTION",
    "VECTOR_INDEX_NAME",
    "setup_schema",
]


def setup_schema(driver: Driver, database: str | None = None) -> None:
    """Create Neo4j uniqueness constraints and the Chunk vector index idempotently.

    Args:
        driver: Active Neo4j driver instance.
        database: Optional target Neo4j database name.
    """
    raise NotImplementedError(
        "Task 1: Implement idempotent Neo4j uniqueness constraints and 384-dim cosine vector index."
    )
