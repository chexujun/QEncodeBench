#!/usr/bin/env python
"""Carve the v1.1 acceptance-pilot subset:
18 tasks per new block (T3p / T4 / F7), 54 total, stratified per cell by
taking the lowest seeds (deterministic).

    T3p: 3sat/vertex_cover/string_match x6
    T4:  3sat 5, vertex_cover 5, subset_sum 4, string_match 4
    F7:  sat_card T1/T2/T3 x6
"""

from __future__ import annotations

import json
import os
import sys

PICKS = {
    ("3sat", 4): 6, ("vertex_cover", 4): 6, ("string_match", 4): 6,
    ("3sat", 5): 5, ("vertex_cover", 5): 5,
    ("subset_sum", 5): 4, ("string_match", 5): 4,
    ("sat_card", 1): 6, ("sat_card", 2): 6, ("sat_card", 3): 6,
}

SRC = "data/frozen_v1_1"
OUT = "data/pilot_v11"


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    out_inst = os.path.join(OUT, "instances.jsonl")
    out_sol = os.path.join(OUT, "solutions.jsonl")
    for p in (out_inst, out_sol):
        if os.path.exists(p):
            print(f"refusing to overwrite {p}", file=sys.stderr)
            return 1

    rows = [json.loads(l) for l in
            open(os.path.join(SRC, "instances_new.jsonl"))]
    sols = {r["task_id"]: r for r in
            (json.loads(l) for l in
             open(os.path.join(SRC, "solutions_new.jsonl")))}

    taken: dict[tuple, int] = {}
    picked = []
    for r in rows:                       # rows are already in seed order
        key = (r["family"], r["tier"])
        if taken.get(key, 0) < PICKS.get(key, 0):
            taken[key] = taken.get(key, 0) + 1
            picked.append(r)

    want = sum(PICKS.values())
    if len(picked) != want:
        print(f"FATAL: picked {len(picked)} != {want}; "
              f"per-cell: {taken}", file=sys.stderr)
        return 1

    with open(out_inst, "w") as fi, open(out_sol, "w") as fs:
        for r in picked:
            fi.write(json.dumps(r) + "\n")
            fs.write(json.dumps(sols[r["task_id"]]) + "\n")
    print(f"pilot_v11: {len(picked)} tasks -> {OUT}")
    for key in PICKS:
        print(f"  {key}: {taken.get(key, 0)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
