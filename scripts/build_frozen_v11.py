#!/usr/bin/env python
"""Build the frozen v1.1 difficulty-escalation rows: +180 instances on top of the immutable v1.0 set.

Quotas:
    T3p (tier 4, zero-slack rolling budget): 3sat/vertex_cover/string_match x20
    T4  (tier 5, scale escalation):  3sat/vertex_cover/subset_sum/string_match x15
    F7  (sat_card, new family):      tiers 1/2/3 x20

Seed domain starts at 200000 (v1.0 uses 0+, fresh sets 100000+).  Every
accepted instance's reference oracle is cross-validated via the full
verifier, duplicates by formal_spec are rejected, and the per-cell yield
(accepted / candidates tried) is reported -- the acceptance bar is a
rejection rate < 80%.

Outputs (refuses to overwrite):
    data/frozen_v1_1/instances_new.jsonl / solutions_new.jsonl  (the +180)
    data/frozen_v1_1/instances.jsonl / solutions.jsonl          (v1.0 + new)
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time

from qencodebench.core.task import tier_label
from qencodebench.generators import get_generator
from qencodebench.pipeline.io import append_jsonl
from qencodebench.verifier import verify_circuit

V11_SEED_BASE = 200_000

# (family, tier) -> quota
QUOTAS = [
    ("3sat", 4, 20), ("vertex_cover", 4, 20), ("string_match", 4, 20),
    ("3sat", 5, 15), ("vertex_cover", 5, 15),
    ("subset_sum", 5, 15), ("string_match", 5, 15),
    ("sat_card", 1, 20), ("sat_card", 2, 20), ("sat_card", 3, 20),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/frozen_v1_1")
    ap.add_argument("--v10", default="data/frozen_v1")
    ap.add_argument("--rejects-log", default="data/generator_rejects.log")
    ap.add_argument("--limit", type=int, default=None,
                    help="cap instances per cell (quick test)")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    new_inst = os.path.join(args.out, "instances_new.jsonl")
    new_sol = os.path.join(args.out, "solutions_new.jsonl")
    for p in (new_inst, new_sol):
        if os.path.exists(p):
            print(f"refusing to overwrite existing {p}", file=sys.stderr)
            return 1

    t0 = time.time()
    total_written = 0
    yields = []
    for family, tier, quota in QUOTAS:
        if args.limit:
            quota = min(quota, args.limit)
        gen = get_generator(family)
        written, seed, seen_specs = 0, V11_SEED_BASE, set()
        seed_cap = V11_SEED_BASE + 200 * quota
        tried = 0
        while written < quota:
            if seed >= seed_cap:
                print(f"FATAL: {family} {tier_label(tier)} exhausted the "
                      f"seed range ({written}/{quota})", flush=True)
                return 1
            tried += 1
            try:
                inst = gen.generate(tier, seed)
            except RuntimeError as e:
                append_jsonl(args.rejects_log, {
                    "family": family, "tier": tier, "seed": seed,
                    "reason": f"exhausted: {e}"})
                seed += 1
                continue
            spec_key = json.dumps(inst.formal_spec, sort_keys=True)
            if spec_key in seen_specs:
                append_jsonl(args.rejects_log, {
                    "family": family, "tier": tier, "seed": seed,
                    "reason": "duplicate_spec"})
                seed += 1
                continue
            sols = gen.classical_solutions(inst)
            ref = gen.reference_oracle(inst)
            res = verify_circuit(ref, inst.n_problem_qubits,
                                 inst.task_id, sols, sample_key="freeze")
            if not res.passed:
                append_jsonl(args.rejects_log, {
                    "family": family, "tier": tier, "seed": seed,
                    "reason": f"reference_failed_L3:{res.fail_reason}"})
                seed += 1
                continue
            seen_specs.add(spec_key)
            append_jsonl(new_inst, json.loads(inst.to_json()))
            append_jsonl(new_sol, {"task_id": inst.task_id,
                                   "solutions": sorted(sols)})
            written += 1
            total_written += 1
            seed += 1
        for r in gen.rejects:
            append_jsonl(args.rejects_log, r)
        rej_rate = 1 - written / tried if tried else 0.0
        yields.append((family, tier, written, tried, rej_rate))
        print(f"{family} {tier_label(tier)}: {written}/{tried} candidates "
              f"(rejection {rej_rate:.0%}) "
              f"[{time.time() - t0:.0f}s elapsed]", flush=True)

    # combined v1.1 = v1.0 rows verbatim + the new rows
    for base, new, name in ((os.path.join(args.v10, "instances.jsonl"),
                             new_inst, "instances.jsonl"),
                            (os.path.join(args.v10, "solutions.jsonl"),
                             new_sol, "solutions.jsonl")):
        combined = os.path.join(args.out, name)
        if os.path.exists(combined):
            print(f"refusing to overwrite existing {combined}",
                  file=sys.stderr)
            return 1
        shutil.copyfile(base, combined)
        with open(new) as fh, open(combined, "a") as out:
            out.write(fh.read())

    print(f"\nYield summary (bar: rejection < 80%):")
    bad = False
    for family, tier, written, tried, rej in yields:
        flag = "  <-- OVER BAR" if rej >= 0.8 else ""
        bad = bad or rej >= 0.8
        print(f"  {family} {tier_label(tier)}: {rej:.0%}{flag}")
    print(f"\nDONE: +{total_written} new instances -> {args.out} "
          f"in {time.time() - t0:.0f}s")
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
