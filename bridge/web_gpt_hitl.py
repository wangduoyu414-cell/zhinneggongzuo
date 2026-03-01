from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from core.file_io import atomic_write_text

RUNS_ROOT = Path("reports") / "runs"
TASKS_DIRNAME = "tasks"
ARTIFACTS_DIRNAME = "artifacts"
PROMPT_FILENAME = "web_gpt_prompt.md"
RESPONSE_FILENAME = "web_gpt_response.md"
CODEX_TASK_FILENAME = "codex_task.md"

_FENCED_BLOCK_RE = re.compile(r"```(?P<lang>[^\n`]*)\n(?P<body>.*?)```", re.DOTALL)


def get_task_dir(run_id: str, task_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return runs_root / run_id / TASKS_DIRNAME / task_id


def get_artifacts_dir(run_id: str, task_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return get_task_dir(run_id, task_id, runs_root=runs_root) / ARTIFACTS_DIRNAME


def emit_prompt(run_id: str, task_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    artifacts_dir = get_artifacts_dir(run_id, task_id, runs_root=runs_root)
    prompt_path = artifacts_dir / PROMPT_FILENAME
    prompt = _build_prompt(run_id=run_id, task_id=task_id, artifacts_dir=artifacts_dir)
    atomic_write_text(prompt_path, prompt, encoding="utf-8")
    return prompt_path


def ingest_response(
    run_id: str,
    task_id: str,
    text: str,
    runs_root: Path = RUNS_ROOT,
) -> dict[str, Any]:
    artifacts_dir = get_artifacts_dir(run_id, task_id, runs_root=runs_root)
    response_path = artifacts_dir / RESPONSE_FILENAME
    codex_task_path = artifacts_dir / CODEX_TASK_FILENAME

    atomic_write_text(response_path, text, encoding="utf-8")

    parsed = _parse_response(text)
    codex_task_text = _build_codex_task_text(
        run_id=run_id,
        task_id=task_id,
        response_text=text,
        parsed=parsed,
    )
    atomic_write_text(codex_task_path, codex_task_text, encoding="utf-8")

    warnings: list[str] = []
    if not text.strip():
        warnings.append("response text is empty")

    return {
        "response_path": str(response_path),
        "codex_task_path": str(codex_task_path),
        "response_char_count": len(text),
        "fenced_code_block_count": len(parsed["fenced_code_blocks"]),
        "warnings": warnings,
        "parsed": parsed,
    }


def _parse_response(text: str) -> dict[str, Any]:
    fenced_code_blocks: list[dict[str, str]] = []
    for match in _FENCED_BLOCK_RE.finditer(text):
        lang = match.group("lang").strip()
        body = match.group("body").strip()
        fenced_code_blocks.append({"language": lang, "content": body})
    return {"fenced_code_blocks": fenced_code_blocks}


def _build_prompt(run_id: str, task_id: str, artifacts_dir: Path) -> str:
    return (
        "# WebGPT HITL Prompt Bridge\n\n"
        f"- run_id: `{run_id}`\n"
        f"- task_id: `{task_id}`\n"
        f"- artifact_dir: `{artifacts_dir.as_posix()}`\n\n"
        "## HITL Steps\n"
        "1. Copy the task prompt you want to ask GPT.\n"
        "2. Paste it into WebGPT manually and run it.\n"
        "3. Copy the full GPT response exactly as-is.\n"
        "4. Call ingest_response(run_id, task_id, text) with the pasted text.\n\n"
        "## Important\n"
        "- Keep the response unmodified to reduce parse drift.\n"
        "- This bridge does not perform browser automation.\n"
    )


def _build_codex_task_text(
    run_id: str,
    task_id: str,
    response_text: str,
    parsed: dict[str, Any],
) -> str:
    fenced_blocks = parsed["fenced_code_blocks"]
    if fenced_blocks:
        primary = fenced_blocks[0]["content"]
        source = "first fenced code block"
    else:
        primary = response_text.strip()
        source = "full response body"

    if not primary:
        primary = "TODO: response was empty; paste complete response and retry."

    return (
        "# Codex Task (Generated from WebGPT HITL)\n\n"
        f"- run_id: `{run_id}`\n"
        f"- task_id: `{task_id}`\n"
        f"- source: {source}\n\n"
        "## Instruction\n"
        f"{primary}\n"
    )

