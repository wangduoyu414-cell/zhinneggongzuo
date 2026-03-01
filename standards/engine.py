from __future__ import annotations

from pathlib import Path
from string import Formatter
from typing import Any

import yaml

DEFAULT_PACK: dict[str, Any] = {
    "version": 1,
    "change_levels": {
        "L0": {"description": "Docs/tests-only style changes", "gate_profile": "fast"},
        "L1": {"description": "Low-risk implementation change", "gate_profile": "full"},
        "L2": {
            "description": "Spec or behavior extension with guarded rollout",
            "gate_profile": "full",
        },
        "L3": {
            "description": "High-risk / stop-the-line candidate",
            "gate_profile": "strict",
            "stop_the_line": True,
        },
    },
    "gates": {
        "profiles": {
            "fast": ["fast_check"],
            "full": ["fast_check", "full_check"],
            "strict": ["fast_check", "full_check"],
        }
    },
    "output_dirs": {
        "reports": "reports",
        "runs": "reports/runs",
        "codex_tasks": "reports/runs/codex_tasks",
    },
    "defaults": {
        "template": "codex_task.txt",
        "include_parallel_impact_section": True,
    },
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_pack(pack_path: str | Path = "standards/pack.yaml") -> dict[str, Any]:
    path = Path(pack_path)
    data: dict[str, Any] = {}
    if path.exists():
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(loaded, dict):
            raise ValueError(f"Pack file must be a mapping: {path}")
        data = loaded
    return _deep_merge(DEFAULT_PACK, data)


def get_gates_for_change_level(
    change_level: str, pack: dict[str, Any] | None = None
) -> list[str]:
    resolved_pack = pack or load_pack()
    level_cfg = resolved_pack.get("change_levels", {}).get(change_level)
    if not isinstance(level_cfg, dict):
        raise ValueError(f"Unknown change level: {change_level}")

    gate_profile = level_cfg.get("gate_profile")
    gates = resolved_pack.get("gates", {}).get("profiles", {}).get(gate_profile)
    if not isinstance(gates, list):
        raise ValueError(
            f"Gate profile '{gate_profile}' missing or invalid for {change_level}"
        )
    return [str(g) for g in gates]


def _extract_template_fields(template: str) -> set[str]:
    fields: set[str] = set()
    for _, field_name, _, _ in Formatter().parse(template):
        if field_name:
            fields.add(field_name)
    return fields


def render_template(template_text: str, context: dict[str, Any]) -> str:
    needed = _extract_template_fields(template_text)
    missing = sorted(field for field in needed if field not in context)
    if missing:
        raise ValueError(f"Template fields missing from context: {', '.join(missing)}")
    return template_text.format(**context)


def generate_codex_task_text(
    *,
    change_level: str,
    context: dict[str, Any] | None = None,
    pack_path: str | Path = "standards/pack.yaml",
    template_name: str | None = None,
) -> str:
    pack = load_pack(pack_path)
    gates = get_gates_for_change_level(change_level, pack)
    level_cfg = pack["change_levels"][change_level]

    tpl_name = template_name or pack["defaults"]["template"]
    template_path = Path(pack_path).parent / "templates" / tpl_name
    template_text = template_path.read_text(encoding="utf-8")

    base_context: dict[str, Any] = {
        "change_level": change_level,
        "gate_profile": level_cfg["gate_profile"],
        "gates_csv": ", ".join(gates),
        "allowed_paths": "standards/* docs/* tests/* config.yaml",
        "forbidden_paths": "core/* flow/* ui_app.py",
        "parallel_impact_assessment": "（同上原文）",
    }
    if context:
        base_context.update(context)

    return render_template(template_text, base_context)
