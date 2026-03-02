from __future__ import annotations

from pathlib import Path
from typing import Literal, Mapping, Protocol, TypedDict

GateMode = Literal["fast", "full"]
GateStatus = Literal["PASSED", "FAILED"]


class GateResult(TypedDict):
    status: GateStatus
    exit_code: int
    gate_log_path: str


class GatePort(Protocol):
    def run(
        self,
        *,
        mode: GateMode,
        cwd: Path,
        env: Mapping[str, str] | None = None,
    ) -> GateResult: ...
