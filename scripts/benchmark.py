"""Local Recall@3 vs. Latency Benchmark Script (Task 6).

Compares three local retrieval strategies against `data/eval_queries.json`:
1. Flat Vector RAG (Baseline)
2. Vector + 2-Hop Graph
3. GraphRAG + Cross-Encoder

Run after completing Tasks 1–6:
    python scripts/benchmark.py
"""

from __future__ import annotations

from graphrag.config import EVAL_QUERIES_PATH, Settings, get_driver
from graphrag.embedder import LocalEmbedder
from graphrag.eval import evaluate_strategy, load_eval_cases
from graphrag.reranker import CrossEncoderReranker
from graphrag.retriever import GraphRetriever


def main() -> None:
    settings = Settings()
    cases = load_eval_cases(EVAL_QUERIES_PATH)

    embedder = LocalEmbedder(model_name=settings.embedding_model)
    reranker = CrossEncoderReranker(model_name=settings.cross_encoder_model)

    with get_driver(settings) as driver:
        retriever = GraphRetriever(
            driver=driver,
            embedder=embedder,
            database=settings.neo4j_database,
        )

        results = [
            evaluate_strategy(
                name="Flat Vector RAG (Baseline)",
                cases=cases,
                retrieve_fn=lambda q: retriever.vector_search(q, top_k=3),
                k=3,
            ),
            evaluate_strategy(
                name="Vector + 2-Hop Graph",
                cases=cases,
                retrieve_fn=lambda q: retriever.hybrid_search(q, seed_k=3, limit=10),
                k=3,
            ),
            evaluate_strategy(
                name="GraphRAG + Cross-Encoder",
                cases=cases,
                retrieve_fn=lambda q: reranker.rerank(
                    q, retriever.hybrid_search(q, seed_k=3, limit=15), top_k=3
                ),
                k=3,
            ),
        ]

    print(f"\n{'Strategy':<30} | {'Recall@3':>10} | {'Avg Latency (ms)':>16} | {'Queries':>7}")
    print("-" * 74)
    for res in results:
        print(
            f"{res.strategy:<30} | {res.recall_at_3 * 100:>9.1f}% | "
            f"{res.avg_latency_ms:>16.1f} | {res.num_queries:>7d}"
        )


if __name__ == "__main__":
    main()
