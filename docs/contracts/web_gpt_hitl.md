# WebGPT HITL Runbook (Minimal)

## Goal
Bridge GPT interaction by manual copy/paste only.

## Steps
1. Generate prompt artifact:
   - call `emit_prompt(run_id, task_id)`
   - open `reports/runs/<run_id>/tasks/<task_id>/artifacts/web_gpt_prompt.md`
2. Manually copy prompt content to WebGPT and submit.
3. Copy the full WebGPT response exactly as returned.
4. Ingest response:
   - call `ingest_response(run_id, task_id, text)`
5. Verify artifacts:
   - `web_gpt_response.md` archived
   - `codex_task.md` generated as next-step instruction placeholder

## Notes
- No browser automation and no automated clicking in this flow.
- If paste is incomplete, rerun ingest with full response text.
