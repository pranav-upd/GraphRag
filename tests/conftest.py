"""Shared pytest fixtures for the Local GraphRAG lab gates."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

import pytest
from neo4j import Driver
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from graphrag.config import INCIDENTS_DIR, Settings, get_driver


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()


@pytest.fixture(scope="session")
def incident_files() -> list[Path]:
    files = sorted(INCIDENTS_DIR.glob("*.md"))
    assert len(files) == 15, f"Expected 15 linked incident docs, found {len(files)}"
    return files


@pytest.fixture(scope="session")
def neo4j_driver(settings: Settings) -> Iterator[Driver]:
    driver = get_driver(settings)
    try:
        driver.verify_connectivity()
    except (ServiceUnavailable, Neo4jError, OSError) as exc:
        driver.close()
        pytest.skip(
            f"Neo4j is not reachable at {settings.neo4j_uri}. "
            f"Start it with `docker compose up -d`. ({exc})"
        )
    yield driver
    driver.close()


@pytest.fixture()
def clean_graph(neo4j_driver: Driver, settings: Settings) -> Iterator[None]:
    """Ensure a clean Document/Chunk/Entity graph before and after a test."""
    with neo4j_driver.session(database=settings.neo4j_database) as session:
        session.run("MATCH (n) WHERE n:Document OR n:Chunk OR n:Entity DETACH DELETE n")
    yield
    with neo4j_driver.session(database=settings.neo4j_database) as session:
        session.run("MATCH (n) WHERE n:Document OR n:Chunk OR n:Entity DETACH DELETE n")
