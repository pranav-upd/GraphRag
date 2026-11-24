"""Pytest Gate for Task 3: GLiNER Zero-Shot Entity Extraction & Normalization."""

from __future__ import annotations

from graphrag.extractor import (
    DEFAULT_ENTITY_LABELS,
    EntityExtractor,
    normalize_entity_name,
)
from graphrag.models import ChunkRecord


def test_normalize_entity_name_canonicalizes_variants() -> None:
    v1 = normalize_entity_name("  checkout-api  ")
    v2 = normalize_entity_name("Checkout-API")
    v3 = normalize_entity_name("checkout-api.")
    assert v1 == v2 == v3
    assert v1 != ""

    assert normalize_entity_name("Maya   Lin") == normalize_entity_name("maya lin")


def test_extractor_strict_schema_and_threshold() -> None:
    extractor = EntityExtractor(threshold=0.35)
    text = (
        "During INC-2025-101, Maya Lin from Data Infra investigated PgBouncer pool "
        "exhaustion on orders-pg-primary affecting checkout-api in us-east-1."
    )

    entities = extractor.extract(text)
    assert len(entities) >= 2, "Expected GLiNER to extract multiple entities from incident text."

    allowed = set(DEFAULT_ENTITY_LABELS)
    for ent in entities:
        assert ent.label in allowed, f"Unexpected label '{ent.label}' outside strict schema."
        assert ent.score >= 0.35
        assert ent.name == normalize_entity_name(ent.name)


def test_extractor_deduplicates_entity_names() -> None:
    extractor = EntityExtractor(threshold=0.35)
    text = (
        "Maya Lin restarted checkout-api. Later, Maya Lin verified that checkout-api "
        "recovered after Maya Lin rolled back the change."
    )
    entities = extractor.extract(text)
    names = [ent.name for ent in entities]
    assert len(names) == len(set(names)), f"Duplicate entity names returned: {names}"


def test_extract_for_chunks_populates_entities() -> None:
    extractor = EntityExtractor(threshold=0.35)
    chunks = [
        ChunkRecord(
            chunk_id="c1",
            doc_id="inc_01",
            index=0,
            text="Hannah Sato mitigated checkout-api timeouts in us-east-1.",
        )
    ]
    result = extractor.extract_for_chunks(chunks)
    assert len(result) == 1
    assert len(result[0].entities) >= 1
