from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AdapterSelection:
    executor_adapter: str = "legacy"
    hitl_adapter: str = "legacy"
    gate_adapter: str = "legacy"


def load_adapter_selection_from_env() -> AdapterSelection:
    return AdapterSelection(
        executor_adapter=os.getenv("EXECUTOR_ADAPTER", "legacy"),
        hitl_adapter=os.getenv("HITL_ADAPTER", "legacy"),
        gate_adapter=os.getenv("GATE_ADAPTER", "legacy"),
    )
