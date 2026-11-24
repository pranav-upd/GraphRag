"""Task 2: Deterministic Chunking & Local Embeddings.

Pytest gate: tests/test_02_embedder.py

Requirements:
1. `make_chunk_id`: Generate a deterministic, collision-resistant ID hash from
   `doc_id`, `chunk_index`, and `text` so re-running chunking produces identical IDs.
2. `chunk_markdown`: Split a Markdown document into non-empty `ChunkRecord` objects
   respecting `chunk_size` and `chunk_overlap` with sequential `index` values.
3. `LocalEmbedder`: Load a local Sentence Transformers model on CPU and encode texts
   into 384-dimensional Python `list[float]` vectors.
"""

from __future__ import annotations

from graphrag.config import EMBEDDING_DIM
from graphrag.models import ChunkRecord

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def make_chunk_id(doc_id: str, chunk_index: int, text: str) -> str:
    """Return a deterministic string identifier for a chunk.

    Calling this function multiple times with the same inputs must always return
    the exact same ID. Changing any input must produce a different ID.
    """
    raise NotImplementedError("Task 2: Implement deterministic chunk ID hashing.")


def chunk_markdown(
    doc_id: str,
    markdown_text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 80,
) -> list[ChunkRecord]:
    """Split a Markdown document into reproducible `ChunkRecord` instances.

    Args:
        doc_id: Unique identifier of the source document (e.g. filename stem).
        markdown_text: Raw Markdown content.
        chunk_size: Maximum target character length per chunk (must be > 0).
        chunk_overlap: Number of overlapping characters between consecutive chunks
            (must be >= 0 and < chunk_size).

    Returns:
        Ordered list of `ChunkRecord` objects with deterministic `chunk_id`s.
    """
    raise NotImplementedError("Task 2: Implement deterministic Markdown chunking.")


class LocalEmbedder:
    """CPU-friendly local embedding encoder backed by Sentence Transformers."""

    def __init__(
        self,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
        device: str = "cpu",
    ) -> None:
        self.model_name = model_name
        self.device = device
        self.embedding_dim = EMBEDDING_DIM
        raise NotImplementedError("Task 2: Initialize the SentenceTransformer model on CPU.")

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Encode a list of strings into 384-dim float vectors."""
        raise NotImplementedError("Task 2: Implement batch text embedding.")

    def embed_query(self, query: str) -> list[float]:
        """Encode a single query string into a 384-dim float vector."""
        raise NotImplementedError("Task 2: Implement single query embedding.")

    def embed_chunks(self, chunks: list[ChunkRecord]) -> list[ChunkRecord]:
        """Populate `.embedding` on each `ChunkRecord` and return the list."""
        raise NotImplementedError("Task 2: Implement chunk embedding.")
