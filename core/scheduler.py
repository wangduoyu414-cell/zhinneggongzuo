from __future__ import annotations

from collections.abc import Mapping


def validate_dag(deps_by_task: Mapping[str, list[str]]) -> None:
    for task_id, deps in deps_by_task.items():
        for dep in deps:
            if dep not in deps_by_task:
                raise ValueError(f"task '{task_id}' has unknown dependency '{dep}'")

    visiting: set[str] = set()
    visited: set[str] = set()

    def dfs(node: str) -> None:
        if node in visiting:
            raise ValueError(f"dependency cycle detected at '{node}'")
        if node in visited:
            return
        visiting.add(node)
        for dep in deps_by_task.get(node, []):
            dfs(dep)
        visiting.remove(node)
        visited.add(node)

    for task_id in deps_by_task:
        dfs(task_id)


def next_runnable_task(
    task_states: Mapping[str, str],
    deps_by_task: Mapping[str, list[str]],
) -> str | None:
    validate_dag(deps_by_task)
    for task_id in sorted(deps_by_task):
        if task_states.get(task_id) != "PENDING":
            continue
        deps = deps_by_task.get(task_id, [])
        if all(task_states.get(dep) == "DONE" for dep in deps):
            return task_id
    return None
