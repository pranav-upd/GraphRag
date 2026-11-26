"""Task 6 Solution (Part A): Cross-Encoder Reranking."""

from __future__ import annotations

from sentence_transformers import CrossEncoder

from graphrag.models import RetrievedChunk

DEFAULT_CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class CrossEncoderReranker:
    """Local Cross-Encoder reranker for precision ordering of retrieved chunks."""

    def __init__(
        self,
        model_name: str = DEFAULT_CROSS_ENCODER_MODEL,
        device: str = "cpu",
    ) -> None:
        self.model_name = model_name
        self.device = device
        self._model = CrossEncoder(model_name, device=device)

    def rerank(
        self,
        query: str,
        candidates: list[RetrievedChunk],
        top_k: int = 3,
    ) -> list[RetrievedChunk]:
        """Rescore candidate chunks with the Cross-Encoder and return top-k results."""
        if not candidates or top_k <= 0:
            return []

        pairs = [(query, cand.text) for cand in candidates]
        scores = self._model.predict(pairs, show_progress_bar=False)

        reranked = [
            RetrievedChunk(
                chunk_id=cand.chunk_id,
                doc_id=cand.doc_id,
                text=cand.text,
                score=float(score),
                source="reranked",
                shared_entities=list(cand.shared_entities),
            )
            for cand, score in zip(candidates, scores)
        ]
        reranked.sort(key=lambda item: item.score, reverse=True)
        return reranked[:top_k]
