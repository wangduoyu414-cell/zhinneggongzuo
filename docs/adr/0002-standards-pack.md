# ADR 0002: Standards Pack Layout

## Status
Accepted

## Date
2026-02-28

## Context
W2 introduces a replaceable standards/policy mechanism without changing existing execution paths.
The repository needs a low-cost way to:
- define ChangeLevel -> gate behavior centrally
- render a reusable Codex task template
- keep current flow stable behind a default-off flag

## Decision
- Add `standards/pack.yaml` as the single policy source for:
  - change level rules (`L0`..`L3`)
  - gate profiles (`fast/full/strict`)
  - output directory conventions
- Add `standards/templates/codex_task.txt` as the minimal task-book template.
- Add `standards/engine.py` to:
  - load and merge pack defaults
  - resolve gates by change level
  - render codex task text with friendly template-field errors
- Keep `enable_standards_engine: false` in `config.yaml` by default.

## Consequences
- Standards are no longer scattered across docs/scripts.
- Future iterations can replace template content and pack fields without touching `core/*`.
- L3 stop-the-line is represented as metadata only in W2; execution behavior is not implemented yet.
