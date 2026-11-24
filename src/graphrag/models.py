"""Shared domain data models used across all GraphRAG labs."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EntityMention:
    """A normalized entity extracted from a chunk of text."""

    name: str
    label: str
    score: float = 1.0


@dataclass
class ChunkRecord:
    """A deterministic document chunk with optional embedding and extracted entities."""

    chunk_id: str
    doc_id: str
    text: str
    index: int
    embedding: list[float] = field(default_factory=list)
    entities: list[EntityMention] = field(default_factory=list)


@dataclass
class RetrievedChunk:
    """A candidate chunk returned by vector, hybrid graph, or reranked retrieval."""

    chunk_id: str
    doc_id: str
    text: str
    score: float
    source: str = "vector"  # e.g., "vector", "graph_hop", "reranked"
    shared_entities: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EvalCase:
    """A single multi-hop evaluation query and its ground-truth relevant documents."""

    query_id: str
    query: str
    relevant_doc_ids: list[str]
    hops: int = 2


@dataclass(frozen=True)
class BenchmarkResult:
    """Aggregated recall and latency metrics for one retrieval strategy."""

    strategy: str
    recall_at_3: float
    avg_latency_ms: float
    num_queries: int
