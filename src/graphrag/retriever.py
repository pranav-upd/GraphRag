"""Task 5: Hybrid Vector + 2-Hop Cypher Search.

Pytest gate: tests/test_05_retriever.py

Requirements:
1. `vector_search`: Baseline flat vector search using Neo4j's vector index
   (`db.index.vector.queryNodes`) to return the top-k matching chunks.
2. `hybrid_search`:
   - Step 1 (Vector Seed): Locate top `seed_k` matching chunks via the vector index.
   - Step 2 (Entity Hop): Traverse shared `Entity` bridges from seed chunks to
     discover connected neighbor chunks (up to 2 hops across shared entities).
   - Step 3 (Fan-Out Cap): Filter out or cap high-degree hub entities exceeding
     `max_entity_degree` and cap neighbors per entity via `max_neighbors_per_entity`.
   - Return deduplicated `RetrievedChunk` candidates ordered by relevance up to `limit`.
"""

from __future__ import annotations

from neo4j import Driver

from graphrag.config import VECTOR_INDEX_NAME
from graphrag.embedder import LocalEmbedder
from graphrag.models import RetrievedChunk


class GraphRetriever:
    """Retrieves candidate chunks using flat vector search or hybrid graph expansion."""

    def __init__(
        self,
        driver: Driver,
        embedder: LocalEmbedder,
        database: str | None = None,
        vector_index_name: str = VECTOR_INDEX_NAME,
    ) -> None:
        self.driver = driver
        self.embedder = embedder
        self.database = database
        self.vector_index_name = vector_index_name

    def vector_search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        """Run flat vector similarity search against the Neo4j Chunk vector index."""
        raise NotImplementedError("Task 5: Implement baseline Neo4j vector search.")

    def hybrid_search(
        self,
        query: str,
        seed_k: int = 3,
        max_entity_degree: int = 10,
        max_neighbors_per_entity: int = 5,
        limit: int = 10,
    ) -> list[RetrievedChunk]:
        """Run vector seed retrieval followed by degree-capped 2-hop entity traversal."""
        raise NotImplementedError(
            "Task 5: Implement hybrid vector + 2-hop Cypher search with fan-out cap."
        )
