#!/usr/bin/env python
"""v1.1 difficulty-escalation acceptance report (paper: escalation table).

Reads the three v11 pilot runs and prints overall + per-block
(T3p / T4 / F7) pass@1 and best-of-3, i.e. the numbers behind the
paper's escalation statistics.
"""

from __future__ import annotations

import collections
import json

RUNS = ("v11_pilot_unit_thinking", "v11_pilot_nsc",
        "v11_pilot_direct_thinking")


def block_of(task_id: str, tier: int) -> str:
    if task_id.startswith("sat_card"):
        return "F7"
    return {4: "T3p", 5: "T4"}[tier]


def main() -> int:
    tier = {}
    for line in open("data/pilot_v11/instances.jsonl"):
        d = json.loads(line)
        tier[d["task_id"]] = d["tier"]

    for run in RUNS:
        by_task = collections.defaultdict(list)
        versions = set()
        for line in open(f"runs/{run}/verify_results.jsonl"):
            r = json.loads(line)
            by_task[r["task_id"]].append(bool(r["pass"]["L3"]))
            versions.add(r.get("verifier_version"))
        n = len(by_task)
        p1 = sum(sum(v) / len(v) for v in by_task.values()) / n
        bo3 = sum(any(v) for v in by_task.values()) / n
        print(f"{run}  [verifier {sorted(versions)}]")
        print(f"  overall: {n} tasks  pass@1={p1:.1%}  bo3={bo3:.1%}")
        blocks = collections.defaultdict(list)
        for t, v in by_task.items():
            blocks[block_of(t, tier[t])].append(v)
        for b in ("T3p", "T4", "F7"):
            vs = blocks[b]
            bp1 = sum(sum(v) / len(v) for v in vs) / len(vs)
            bbo = sum(any(v) for v in vs) / len(vs)
            print(f"  {b}: {len(vs)} tasks  pass@1={bp1:.1%}  bo3={bbo:.1%}")
    return 0


if __name__ == "__main__":
    return_code = main()
    raise SystemExit(return_code)
