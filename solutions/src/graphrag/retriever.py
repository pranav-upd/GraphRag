"""Task 5 Solution: Hybrid Vector + 2-Hop Cypher Search."""

from __future__ import annotations

from neo4j import Driver

from graphrag.config import VECTOR_INDEX_NAME
from graphrag.embedder import LocalEmbedder
from graphrag.models import RetrievedChunk

VECTOR_SEARCH_CYPHER = """
CALL db.index.vector.queryNodes($index_name, $top_k, $embedding)
YIELD node AS c, score
MATCH (d:Document)-[:HAS_CHUNK]->(c)
RETURN c.id AS chunk_id,
       d.id AS doc_id,
       c.text AS text,
       score
ORDER BY score DESC
""".strip()

HYBRID_TWO_HOP_CYPHER = """
CALL db.index.vector.queryNodes($index_name, $seed_k, $embedding)
YIELD node AS seed, score AS seed_score
MATCH (sd:Document)-[:HAS_CHUNK]->(seed)
WITH collect({
    chunk_id: seed.id,
    doc_id: sd.id,
    text: seed.text,
    score: seed_score,
    source: 'vector',
    shared_entities: []
}) AS seed_rows, collect({node: seed, score: seed_score}) AS seeds

UNWIND seeds AS s
WITH seed_rows, s.node AS seed, s.score AS seed_score
OPTIONAL MATCH (seed)-[:MENTIONS]->(e1:Entity)<-[:MENTIONS]-(n1:Chunk)
WHERE n1 <> seed
  AND COUNT { (e1)<-[:MENTIONS]-(:Chunk) } <= $max_entity_degree
WITH seed_rows, seed, seed_score, e1, collect(DISTINCT n1)[0..$max_neighbors_per_entity] AS hop1_nodes
UNWIND (CASE WHEN size(hop1_nodes) = 0 THEN [NULL] ELSE hop1_nodes END) AS n1
OPTIONAL MATCH (d1:Document)-[:HAS_CHUNK]->(n1)
WITH seed_rows, seed, seed_score, e1, n1, d1

OPTIONAL MATCH (n1)-[:MENTIONS]->(e2:Entity)<-[:MENTIONS]-(n2:Chunk)
WHERE n1 IS NOT NULL
  AND e2 <> e1
  AND n2 <> seed
  AND n2 <> n1
  AND COUNT { (e2)<-[:MENTIONS]-(:Chunk) } <= $max_entity_degree
WITH seed_rows, seed_score, e1, n1, d1, e2, collect(DISTINCT n2)[0..$max_neighbors_per_entity] AS hop2_nodes
UNWIND (CASE WHEN size(hop2_nodes) = 0 THEN [NULL] ELSE hop2_nodes END) AS n2
OPTIONAL MATCH (d2:Document)-[:HAS_CHUNK]->(n2)

WITH seed_rows,
     collect(
        CASE WHEN n1 IS NOT NULL THEN {
            chunk_id: n1.id,
            doc_id: d1.id,
            text: n1.text,
            score: seed_score * 0.85,
            source: 'graph_hop',
            shared_entities: [e1.name]
        } END
     ) AS hop1_rows,
     collect(
        CASE WHEN n2 IS NOT NULL THEN {
            chunk_id: n2.id,
            doc_id: d2.id,
            text: n2.text,
            score: seed_score * 0.70,
            source: 'graph_hop',
            shared_entities: [e1.name, e2.name]
        } END
     ) AS hop2_rows

WITH [r IN (seed_rows + hop1_rows + hop2_rows) WHERE r IS NOT NULL] AS all_rows
UNWIND all_rows AS row
RETURN row.chunk_id AS chunk_id,
       row.doc_id AS doc_id,
       row.text AS text,
       max(row.score) AS score,
       collect(DISTINCT row.source) AS sources,
       reduce(acc = [], ents IN collect(row.shared_entities) | acc + ents) AS shared_entities
ORDER BY score DESC
LIMIT $limit
""".strip()


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
        embedding = self.embedder.embed_query(query)
        with self.driver.session(database=self.database) as session:
            rows = session.run(
                VECTOR_SEARCH_CYPHER,
                index_name=self.vector_index_name,
                top_k=top_k,
                embedding=embedding,
            ).data()

        return [
            RetrievedChunk(
                chunk_id=row["chunk_id"],
                doc_id=row["doc_id"],
                text=row["text"],
                score=float(row["score"]),
                source="vector",
            )
            for row in rows
        ]

    def hybrid_search(
        self,
        query: str,
        seed_k: int = 3,
        max_entity_degree: int = 10,
        max_neighbors_per_entity: int = 5,
        limit: int = 10,
    ) -> list[RetrievedChunk]:
        """Run vector seed retrieval followed by degree-capped 2-hop entity traversal."""
        embedding = self.embedder.embed_query(query)
        with self.driver.session(database=self.database) as session:
            rows = session.run(
                HYBRID_TWO_HOP_CYPHER,
                index_name=self.vector_index_name,
                seed_k=seed_k,
                embedding=embedding,
                max_entity_degree=max_entity_degree,
                max_neighbors_per_entity=max_neighbors_per_entity,
                limit=limit,
            ).data()

        results: list[RetrievedChunk] = []
        for row in rows:
            sources = row.get("sources") or []
            source = "vector" if "vector" in sources else "graph_hop"
            shared = sorted({e for e in (row.get("shared_entities") or []) if e})
            results.append(
                RetrievedChunk(
                    chunk_id=row["chunk_id"],
                    doc_id=row["doc_id"],
                    text=row["text"],
                    score=float(row["score"]),
                    source=source,
                    shared_entities=shared,
                )
            )
        return results
