from __future__ import annotations

from pathlib import Path
from typing import Protocol, TypedDict


class HitlReceiveResult(TypedDict):
    hitl_response_path: str
    received: bool


class HitlPort(Protocol):
    def emit_prompt(self, hitl_prompt_path: Path) -> Path: ...

    def receive_response(self, hitl_prompt_path: Path) -> HitlReceiveResult: ...
