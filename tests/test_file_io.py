from __future__ import annotations

import threading
from pathlib import Path

from core.file_io import atomic_write_json, atomic_write_text, read_json, read_text


def test_atomic_write_text_never_reads_partial_content(tmp_path: Path) -> None:
    path = tmp_path / "atomic.txt"
    content_a = "A" * 10_000
    content_b = "B" * 20_000
    atomic_write_text(path, content_a)

    stop = threading.Event()
    errors: list[str] = []

    def writer() -> None:
        for _ in range(40):
            atomic_write_text(path, content_b)
            atomic_write_text(path, content_a)
        stop.set()

    def reader() -> None:
        while not stop.is_set():
            data = read_text(path)
            if data not in (content_a, content_b):
                errors.append("read partial content")
                stop.set()
                return

    tw = threading.Thread(target=writer)
    tr = threading.Thread(target=reader)
    tw.start()
    tr.start()
    tw.join(timeout=10)
    stop.set()
    tr.join(timeout=10)

    assert not errors
    assert not tw.is_alive()
    assert not tr.is_alive()


def test_atomic_write_json_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "payload.json"
    payload = {"a": 1, "b": "x"}
    atomic_write_json(path, payload)
    assert read_json(path) == payload
