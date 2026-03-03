---
id: INS-M4-05
related_rfc: RFC-M4-00
owner: xuxuyang
date: 2026-03-03
project: agent-workflow-kernel
risk: mid
---

# INS-M4-05: repo_local_only offline cleanup

## 1. Goal
- Enforce local-only workflow operation.
- Archive remote-CI references instead of deleting information.
- Keep local gate scripts as the source of truth.

## 2. Scope
Allowed paths only:
- `.github/workflows/**` (archive move)
- `docs/**` (archive + notes + encoding audit)
- `scripts/**` (no semantic change in this slice)

## 3. Actions
- Move `.github/workflows/*` to `docs/ci_examples/workflows/`.
- Move remote-truth docs to `docs/archive/remote_ci_notes/`.
- Add `docs/ci_examples/README.md` to clarify local gate source of truth.
- UTF-8 policy:
  - fix only files that fail strict UTF-8 decode (none found in this run)
  - list mojibake-like files for manual review (`docs/change_spec.md`)

## 4. Validation
- `powershell -ExecutionPolicy Bypass -File scripts/fast_check.ps1`
- `python -m pytest -q`
