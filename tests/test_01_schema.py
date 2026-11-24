"""Pytest Gate for Task 1: Neo4j Constraints & Vector Index."""

from __future__ import annotations

from neo4j import Driver

from graphrag.config import Settings
from graphrag.schema import (
    EMBEDDING_DIM,
    SIMILARITY_FUNCTION,
    VECTOR_INDEX_NAME,
    setup_schema,
)


def test_setup_schema_is_idempotent(neo4j_driver: Driver, settings: Settings) -> None:
    """Running setup_schema twice must succeed without raising errors."""
    setup_schema(neo4j_driver, database=settings.neo4j_database)
    setup_schema(neo4j_driver, database=settings.neo4j_database)


def test_uniqueness_constraints_exist(neo4j_driver: Driver, settings: Settings) -> None:
    """Document.id, Chunk.id, and Entity.name must each have a uniqueness constraint."""
    setup_schema(neo4j_driver, database=settings.neo4j_database)

    with neo4j_driver.session(database=settings.neo4j_database) as session:
        rows = session.run("SHOW CONSTRAINTS").data()

    found = {
        (tuple(row.get("labelsOrTypes") or []), tuple(row.get("properties") or []))
        for row in rows
        if row.get("type") == "UNIQUENESS"
    }

    expected = {
        (("Document",), ("id",)),
        (("Chunk",), ("id",)),
        (("Entity",), ("name",)),
    }
    missing = expected - found
    assert not missing, f"Missing required uniqueness constraints: {missing}"


def test_chunk_vector_index_exists(neo4j_driver: Driver, settings: Settings) -> None:
    """A 384-dim cosine vector index named VECTOR_INDEX_NAME must exist on Chunk.embedding."""
    setup_schema(neo4j_driver, database=settings.neo4j_database)

    with neo4j_driver.session(database=settings.neo4j_database) as session:
        rows = session.run(
            "SHOW INDEXES YIELD name, type, labelsOrTypes, properties, options "
            "WHERE name = $name",
            name=VECTOR_INDEX_NAME,
        ).data()

    assert len(rows) == 1, f"Vector index '{VECTOR_INDEX_NAME}' not found."
    idx = rows[0]
    assert idx["type"] == "VECTOR"
    assert idx["labelsOrTypes"] == ["Chunk"]
    assert idx["properties"] == ["embedding"]

    index_config = (idx.get("options") or {}).get("indexConfig", {})
    assert index_config.get("vector.dimensions") == EMBEDDING_DIM
    assert str(index_config.get("vector.similarity_function", "")).lower() == SIMILARITY_FUNCTION
