"""JSONL I/O helpers for instances, solutions, and run artifacts."""

from __future__ import annotations

import json
import os

from qencodebench.core.task import TaskInstance


def append_jsonl(path: str, row: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_instances(path: str) -> list[TaskInstance]:
    return [TaskInstance.from_dict(r) for r in read_jsonl(path)]


def load_solutions(path: str) -> dict[str, set[int]]:
    return {r["task_id"]: set(r["solutions"]) for r in read_jsonl(path)}
