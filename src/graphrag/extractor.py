"""Task 3: GLiNER Zero-Shot Entity Extraction & Normalization.

Pytest gate: tests/test_03_extractor.py

Requirements:
1. `normalize_entity_name`: Canonicalize extracted entity spans (trim whitespace,
   collapse internal whitespace, normalize casing/punctuation) so equivalent mentions
   map to a single canonical `Entity.name`.
2. `EntityExtractor`: Run single-pass zero-shot NER on CPU using GLiNER with a
   strict, deterministic label schema (`DEFAULT_ENTITY_LABELS`), deduplicating
   entities per chunk while keeping the highest-confidence mention.
"""

from __future__ import annotations

from graphrag.models import ChunkRecord, EntityMention

DEFAULT_GLINER_MODEL = "urchade/gliner_small-v2.1"

DEFAULT_ENTITY_LABELS: list[str] = [
    "service",
    "database",
    "person",
    "team",
    "incident",
    "region",
    "technology",
]


def normalize_entity_name(name: str) -> str:
    """Canonicalize an entity string before graph ingestion.

    Examples of expected behavior:
    - Trims leading/trailing whitespace and stray surrounding punctuation.
    - Collapses repeated internal whitespace to a single space.
    - Produces a consistent canonical casing so duplicate Entity nodes are avoided.
    """
    raise NotImplementedError("Task 3: Implement entity name normalization.")


class EntityExtractor:
    """Local zero-shot NER extractor using GLiNER."""

    def __init__(
        self,
        model_name: str = DEFAULT_GLINER_MODEL,
        labels: list[str] | None = None,
        threshold: float = 0.45,
    ) -> None:
        self.model_name = model_name
        self.labels = list(labels) if labels is not None else list(DEFAULT_ENTITY_LABELS)
        self.threshold = threshold
        raise NotImplementedError("Task 3: Load the local GLiNER model.")

    def extract(
        self,
        text: str,
        labels: list[str] | None = None,
        threshold: float | None = None,
    ) -> list[EntityMention]:
        """Extract, normalize, and deduplicate entity mentions from `text`.

        Only labels present in the requested schema may be returned.
        """
        raise NotImplementedError("Task 3: Implement GLiNER span extraction & deduplication.")

    def extract_for_chunks(self, chunks: list[ChunkRecord]) -> list[ChunkRecord]:
        """Populate `.entities` on each `ChunkRecord` and return the list."""
        raise NotImplementedError("Task 3: Implement batch extraction for ChunkRecords.")
