# Local GraphRAG in Python

**Neo4j, GLiNER, and Sentence Transformers — zero cloud APIs required.**

This is the **starter workspace** for the 105-minute guided project course. Complete each task in order and verify your work against its corresponding `pytest` gate before moving on.

## Curriculum & Pytest Gates

| Task | Engineering Focus | Time | Starter Module | Pytest Gate |
| :--- | :--- | :---: | :--- | :--- |
| **Task 1** | Neo4j constraints & vector index | 15 min | `src/graphrag/schema.py` | `tests/test_01_schema.py` |
| **Task 2** | Deterministic chunking & embeddings | 15 min | `src/graphrag/embedder.py` | `tests/test_02_embedder.py` |
| **Task 3** | GLiNER zero-shot entity extraction | 20 min | `src/graphrag/extractor.py` | `tests/test_03_extractor.py` |
| **Task 4** | Batched UNWIND Cypher ingestion | 20 min | `src/graphrag/ingest.py` | `tests/test_04_ingest.py` |
| **Task 5** | Hybrid vector + 2-hop Cypher search | 20 min | `src/graphrag/retriever.py` | `tests/test_05_retriever.py` |
| **Task 6** | Cross-Encoder reranking & benchmark | 15 min | `src/graphrag/reranker.py`, `src/graphrag/eval.py` | `tests/test_06_eval.py` |

## Project Structure

```text
.
├── data/
│   ├── incidents/              # 15 linked incident Markdown documents
│   └── eval_queries.json       # Multi-hop evaluation queries & ground truth
├── scripts/
│   └── benchmark.py            # Local Recall@3 vs. latency benchmark CLI
├── src/
│   └── graphrag/
│       ├── __init__.py
│       ├── config.py           # Environment & model configuration
│       ├── models.py           # Shared dataclasses (Document, Chunk, Entity, Result)
│       ├── schema.py           # Task 1: Neo4j constraints & vector index
│       ├── embedder.py         # Task 2: Deterministic chunking & embeddings
│       ├── extractor.py        # Task 3: GLiNER zero-shot NER & normalization
│       ├── ingest.py           # Task 4: Batched UNWIND Cypher ingestion
│       ├── retriever.py        # Task 5: Hybrid vector + 2-hop Cypher search
│       ├── reranker.py         # Task 6: Cross-Encoder reranking
│       └── eval.py             # Task 6: Recall@k & benchmark evaluation
├── tests/
│   ├── conftest.py             # Shared pytest fixtures (Neo4j driver, sample data)
│   ├── test_01_schema.py
│   ├── test_02_embedder.py
│   ├── test_03_extractor.py
│   ├── test_04_ingest.py
│   ├── test_05_retriever.py
│   └── test_06_eval.py
├── docker-compose.yml          # Local Neo4j 5.x instance
├── pyproject.toml
└── .env.example
```

## Quickstart

### 1. Start Local Neo4j

```bash
cp .env.example .env
docker compose up -d
```

Verify Neo4j is running at `http://localhost:7474` (default credentials: `neo4j` / `graphrag_local`).

### 2. Install Python Dependencies

```CLI
git clone https://github.com/pranav-upd/GraphRag.git
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS / Linux:
# source .venv/bin/activate

pip install -e ".[dev]"
```
### Complete each exercise in src/graphrag as they are covered in in the course

### 3. Run Pytest Gates Step-by-Step

Run each gate as you complete the corresponding task:

```bash
pytest tests/test_01_schema.py
pytest tests/test_02_embedder.py
pytest tests/test_03_extractor.py
pytest tests/test_04_ingest.py
pytest tests/test_05_retriever.py
pytest tests/test_06_eval.py
```

### 4. Run the Local Benchmark (After Task 6)

```bash
python scripts/benchmark.py
```
