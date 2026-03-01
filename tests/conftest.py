from __future__ import annotations

from pathlib import Path


def pytest_ignore_collect(collection_path: Path, config: object) -> bool:
    parts = set(collection_path.parts)
    return ".venv" in parts or "reports" in parts

