"""Runtime configuration and Neo4j driver helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from neo4j import Driver, GraphDatabase

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
INCIDENTS_DIR = DATA_DIR / "incidents"
EVAL_QUERIES_PATH = DATA_DIR / "eval_queries.json"

VECTOR_INDEX_NAME = "chunk_embedding_idx"
EMBEDDING_DIM = 384
SIMILARITY_FUNCTION = "cosine"


@dataclass(frozen=True)
class Settings:
    """Connection and local model settings loaded from environment variables."""

    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "graphrag_local")
    neo4j_database: str = os.getenv("NEO4J_DATABASE", "neo4j")
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    gliner_model: str = os.getenv("GLINER_MODEL", "urchade/gliner_small-v2.1")
    cross_encoder_model: str = os.getenv(
        "CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"
    )


def get_driver(settings: Settings | None = None) -> Driver:
    """Create a Neo4j Bolt driver from the provided or default settings."""
    cfg = settings or Settings()
    return GraphDatabase.driver(
        cfg.neo4j_uri,
        auth=(cfg.neo4j_user, cfg.neo4j_password),
    )
