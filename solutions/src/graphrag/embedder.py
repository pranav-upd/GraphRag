"""Task 2 Solution: Deterministic Chunking & Local Embeddings."""

from __future__ import annotations

import hashlib

from sentence_transformers import SentenceTransformer

from graphrag.config import EMBEDDING_DIM
from graphrag.models import ChunkRecord

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def make_chunk_id(doc_id: str, chunk_index: int, text: str) -> str:
    """Return a deterministic SHA-256 hex digest prefix for a chunk."""
    payload = f"{doc_id}::{chunk_index}::{text}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:24]


def chunk_markdown(
    doc_id: str,
    markdown_text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 80,
) -> list[ChunkRecord]:
    """Split a Markdown document into reproducible `ChunkRecord` instances."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be >= 0 and < chunk_size")

    cleaned = markdown_text.replace("\r\n", "\n").strip()
    if not cleaned:
        return []

    chunks: list[ChunkRecord] = []
    start = 0
    text_len = len(cleaned)
    idx = 0

    while start < text_len:
        end = min(start + chunk_size, text_len)

        # Prefer splitting on a paragraph, newline, or word boundary when not at EOF.
        if end < text_len:
            split_pos = cleaned.rfind("\n\n", start, end)
            if split_pos == -1 or split_pos <= start + chunk_size // 3:
                split_pos = cleaned.rfind("\n", start, end)
            if split_pos == -1 or split_pos <= start + chunk_size // 3:
                split_pos = cleaned.rfind(" ", start, end)
            if split_pos > start + chunk_size // 3:
                end = split_pos

        piece = cleaned[start:end].strip()
        if piece:
            chunks.append(
                ChunkRecord(
                    chunk_id=make_chunk_id(doc_id, idx, piece),
                    doc_id=doc_id,
                    text=piece,
                    index=idx,
                )
            )
            idx += 1

        if end >= text_len:
            break

        next_start = max(start + 1, end - chunk_overlap)
        start = next_start

    return chunks


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
        self._model = SentenceTransformer(model_name, device=device)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Encode a list of strings into 384-dim float vectors."""
        if not texts:
            return []
        matrix = self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [[float(v) for v in row] for row in matrix]

    def embed_query(self, query: str) -> list[float]:
        """Encode a single query string into a 384-dim float vector."""
        return self.embed_texts([query])[0]

    def embed_chunks(self, chunks: list[ChunkRecord]) -> list[ChunkRecord]:
        """Populate `.embedding` on each `ChunkRecord` and return the list."""
        if not chunks:
            return chunks
        vectors = self.embed_texts([c.text for c in chunks])
        for chunk, vec in zip(chunks, vectors):
            chunk.embedding = vec
        return chunks
