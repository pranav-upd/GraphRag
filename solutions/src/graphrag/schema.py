"""Task 1 Solution: Neo4j Constraints & Vector Index."""

from __future__ import annotations

from neo4j import Driver

from graphrag.config import EMBEDDING_DIM, SIMILARITY_FUNCTION, VECTOR_INDEX_NAME

__all__ = [
    "EMBEDDING_DIM",
    "SIMILARITY_FUNCTION",
    "VECTOR_INDEX_NAME",
    "setup_schema",
]

SCHEMA_STATEMENTS: tuple[str, ...] = (
    "CREATE CONSTRAINT document_id_unique IF NOT EXISTS "
    "FOR (d:Document) REQUIRE d.id IS UNIQUE",
    "CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS "
    "FOR (c:Chunk) REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT entity_name_unique IF NOT EXISTS "
    "FOR (e:Entity) REQUIRE e.name IS UNIQUE",
    f"""
    CREATE VECTOR INDEX {VECTOR_INDEX_NAME} IF NOT EXISTS
    FOR (c:Chunk) ON (c.embedding)
    OPTIONS {{
        indexConfig: {{
            `vector.dimensions`: {EMBEDDING_DIM},
            `vector.similarity_function`: '{SIMILARITY_FUNCTION}'
        }}
    }}
    """.strip(),
)


def setup_schema(driver: Driver, database: str | None = None) -> None:
    """Create Neo4j uniqueness constraints and the Chunk vector index idempotently."""
    with driver.session(database=database) as session:
        for statement in SCHEMA_STATEMENTS:
            session.run(statement).consume()
