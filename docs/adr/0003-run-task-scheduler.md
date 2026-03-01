# ADR 0003: Run/Task Scheduler Starts Serial

## Status
Accepted

## Context
W4 introduces run/task orchestration with dependency-aware scheduling and a Codex CLI executor.
The mainline path requires deterministic behavior, idempotent artifacts, and clear failure handling.
True parallel execution increases race-condition risk around task state transitions and artifact writes.

## Decision
Implement scheduler/executor integration in serial mode first.

- `enable_true_concurrency` is present in `config.yaml` and defaults to `false`.
- `core/scheduler.py` provides DAG validation and next runnable task selection.
- `flow/graph.py` executes one runnable task at a time while preserving dependency ordering.

## Consequences
- Pros:
  - deterministic state/event ordering
  - simpler idempotency guarantees for `run_state.json` and `events.jsonl`
  - lower regression risk on the core path
- Cons:
  - throughput is lower than a parallel dispatcher
  - later work is needed to safely fan out runnable tasks

## Follow-up
When enabling true concurrency, add:
1. task-level locks or optimistic concurrency control for state writes
2. bounded worker pool and backpressure policy
3. race-focused tests for WAIT/INGEST and retries
