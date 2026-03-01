from pathlib import Path

import yaml

from standards.engine import (
    generate_codex_task_text,
    get_gates_for_change_level,
    load_pack,
    render_template,
)


def test_load_pack_defaults_when_file_missing(tmp_path: Path) -> None:
    pack = load_pack(tmp_path / "missing_pack.yaml")
    assert pack["version"] == 1
    assert pack["gates"]["profiles"]["full"] == ["fast_check", "full_check"]
    assert pack["defaults"]["template"] == "codex_task.txt"


def test_load_pack_merges_with_default_values(tmp_path: Path) -> None:
    pack_file = tmp_path / "pack.yaml"
    pack_file.write_text(
        yaml.safe_dump(
            {
                "change_levels": {
                    "L2": {
                        "description": "custom",
                        "gate_profile": "strict",
                    }
                }
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    pack = load_pack(pack_file)
    assert pack["change_levels"]["L2"]["description"] == "custom"
    assert pack["change_levels"]["L2"]["gate_profile"] == "strict"
    assert pack["gates"]["profiles"]["strict"] == ["fast_check", "full_check"]


def test_get_gates_for_change_level_defaults() -> None:
    gates = get_gates_for_change_level("L2")
    assert gates == ["fast_check", "full_check"]


def test_render_template_friendly_missing_field() -> None:
    try:
        render_template("X={x} Y={y}", {"x": 1})
    except ValueError as exc:
        assert "y" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing template field")


def test_generate_codex_task_text_from_pack() -> None:
    text = generate_codex_task_text(change_level="L2")
    assert "ChangeLevel: L2" in text
    assert "Gates: fast_check, full_check" in text
    assert "并行影响评估/门禁" in text
