# WebGPT HITL Bridge Spec (W3)

## Scope
- Human-in-the-loop file bridge only.
- No browser automation, no click control, no anti-detection or risk-control bypass behavior.

## Feature Flag
- `config.yaml`
  - `enable_web_gpt_hitl: false` by default.

## Directory Contract
- Task artifact root:
  - `reports/runs/<run_id>/tasks/<task_id>/artifacts/`

## Files
- Prompt file:
  - `web_gpt_prompt.md`
  - Produced by: `emit_prompt(run_id, task_id)`
- Response file:
  - `web_gpt_response.md`
  - Produced by: `ingest_response(run_id, task_id, text)`
- Next-step instruction book:
  - `codex_task.md`
  - Produced by: `ingest_response(run_id, task_id, text)`

## Prompt Template Fields
- `run_id` (string)
- `task_id` (string)
- `artifact_dir` (string path)
- `copy_instructions` (fixed text, asks user to copy/paste original GPT response)

## Ingest Output (minimal parse)
- Keep full original text as-is in `web_gpt_response.md`.
- Optional minimal extraction:
  - fenced code blocks (language + body)
- Generate `codex_task.md` as placeholder:
  - If fenced blocks exist, use first fenced block as main instruction body.
  - Else use full response body.

## Error Handling
- Empty/blank response:
  - Save original text anyway.
  - Emit `warnings` with `response text is empty`.
- Truncated risk (best effort):
  - Record `response_char_count` for operator inspection.

