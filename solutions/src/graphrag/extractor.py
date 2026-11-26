"""Task 3 Solution: GLiNER Zero-Shot Entity Extraction & Normalization."""

from __future__ import annotations

import re

from gliner import GLiNER

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

_EDGE_PUNCT = " \t\n\r.,;:!?'\"`()[]{}<>"


def normalize_entity_name(name: str) -> str:
    """Canonicalize an entity string before graph ingestion."""
    cleaned = name.strip(_EDGE_PUNCT)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.lower()


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
        self._model = GLiNER.from_pretrained(model_name)

    def extract(
        self,
        text: str,
        labels: list[str] | None = None,
        threshold: float | None = None,
    ) -> list[EntityMention]:
        """Extract, normalize, and deduplicate entity mentions from `text`."""
        if not text or not text.strip():
            return []

        active_labels = list(labels) if labels is not None else list(self.labels)
        active_threshold = self.threshold if threshold is None else threshold
        allowed = set(active_labels)

        raw_entities = self._model.predict_entities(
            text,
            active_labels,
            threshold=active_threshold,
        )

        best_by_name: dict[str, EntityMention] = {}
        for item in raw_entities:
            label = str(item.get("label", ""))
            score = float(item.get("score", 0.0))
            if label not in allowed or score < active_threshold:
                continue

            canonical = normalize_entity_name(str(item.get("text", "")))
            if not canonical:
                continue

            existing = best_by_name.get(canonical)
            if existing is None or score > existing.score:
                best_by_name[canonical] = EntityMention(
                    name=canonical,
                    label=label,
                    score=score,
                )

        return sorted(
            best_by_name.values(),
            key=lambda ent: (-ent.score, ent.name),
        )

    def extract_for_chunks(self, chunks: list[ChunkRecord]) -> list[ChunkRecord]:
        """Populate `.entities` on each `ChunkRecord` and return the list."""
        for chunk in chunks:
            chunk.entities = self.extract(chunk.text)
        return chunks
