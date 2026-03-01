from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any


def atomic_write_text(path: os.PathLike[str] | str, content: str, encoding: str = "utf-8") -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    fd, temp_path = tempfile.mkstemp(prefix=f"{target.name}.", suffix=".tmp", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding=encoding, newline="\n") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        last_error: PermissionError | None = None
        for attempt in range(20):
            try:
                os.replace(temp_path, target)
                last_error = None
                break
            except PermissionError as exc:
                last_error = exc
                time.sleep(0.005 * (attempt + 1))
        if last_error is not None:
            raise last_error
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def atomic_write_json(
    path: os.PathLike[str] | str,
    payload: Any,
    *,
    ensure_ascii: bool = False,
    indent: int = 2,
) -> None:
    text = json.dumps(payload, ensure_ascii=ensure_ascii, indent=indent, sort_keys=True)
    atomic_write_text(path, text + "\n", encoding="utf-8")


def read_text(path: os.PathLike[str] | str, encoding: str = "utf-8") -> str:
    target = Path(path)
    last_error: PermissionError | None = None
    for attempt in range(20):
        try:
            return target.read_text(encoding=encoding)
        except PermissionError as exc:
            last_error = exc
            time.sleep(0.005 * (attempt + 1))
    if last_error is not None:
        raise last_error
    return target.read_text(encoding=encoding)


def read_json(path: os.PathLike[str] | str, encoding: str = "utf-8") -> Any:
    return json.loads(read_text(path, encoding=encoding))
