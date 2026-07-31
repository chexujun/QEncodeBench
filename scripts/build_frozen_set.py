#!/usr/bin/env python
"""Build the frozen v1.0 task set: 480 instances
(3sat/coloring 100 each; the other four families 70 each), tier-balanced.

Every accepted instance's reference oracle is cross-validated against the
classical solver via method A (plus exhaustive on a 5% hash-selected spot
sample).  Rejected candidates are appended to data/generator_rejects.log.

Usage:
    python scripts/build_frozen_set.py [--out data/frozen_v1] [--fresh TAG]

--fresh generates a fresh set with a disjoint seed range instead.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

from qencodebench.core.task import TaskInstance  # noqa: F401
from qencodebench.generators import get_generator
from qencodebench.pipeline.io import append_jsonl
from qencodebench.verifier import verify_circuit

FAMILY_QUOTAS = {
    "3sat": 100, "coloring": 100,
    "vertex_cover": 70, "subset_sum": 70,
    "latin_square": 70, "string_match": 70,
}
FRESH_SEED_BASE = 100_000     # fresh sets never overlap frozen seeds


def tier_split(total: int) -> dict[int, int]:
    base = total // 3
    return {1: total - 2 * base, 2: base, 3: base}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/frozen_v1")
    ap.add_argument("--fresh", default=None,
                    help="tag for a fresh set, e.g. 20260810")
    ap.add_argument("--rejects-log", default="data/generator_rejects.log")
    ap.add_argument("--limit", type=int, default=None,
                    help="cap instances per family x tier (quick test)")
    args = ap.parse_args()

    out_dir = args.out if not args.fresh else f"data/fresh_{args.fresh}"
    seed_base = 0 if not args.fresh else FRESH_SEED_BASE
    os.makedirs(out_dir, exist_ok=True)
    inst_path = os.path.join(out_dir, "instances.jsonl")
    sol_path = os.path.join(out_dir, "solutions.jsonl")
    for p in (inst_path, sol_path):
        if os.path.exists(p):
            print(f"refusing to overwrite existing {p}", file=sys.stderr)
            return 1

    t0 = time.time()
    total_written = 0
    for family, quota in FAMILY_QUOTAS.items():
        for tier, n_needed in tier_split(quota).items():
            if args.limit:
                n_needed = min(n_needed, args.limit)
            gen = get_generator(family)
            written, seed, seen_specs = 0, seed_base, set()
            seed_cap = seed_base + 200 * n_needed
            while written < n_needed:
                if seed >= seed_cap:
                    print(f"FATAL: {family} T{tier} exhausted the seed "
                          f"range ({written}/{n_needed} written) -- the "
                          "parameter space is too small for the quota", flush=True)
                    return 1
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
                                     inst.task_id, sols,
                                     sample_key="freeze")
                if not res.passed:
                    append_jsonl(args.rejects_log, {
                        "family": family, "tier": tier, "seed": seed,
                        "reason": f"reference_failed_L3:{res.fail_reason}"})
                    seed += 1
                    continue
                seen_specs.add(spec_key)
                append_jsonl(inst_path, json.loads(inst.to_json()))
                append_jsonl(sol_path, {"task_id": inst.task_id,
                                        "solutions": sorted(sols)})
                written += 1
                total_written += 1
                seed += 1
            for r in gen.rejects:
                append_jsonl(args.rejects_log, r)
            print(f"{family} T{tier}: {written} instances "
                  f"(seeds up to {seed - 1}, "
                  f"{len(gen.rejects)} candidate rejects) "
                  f"[{time.time() - t0:.0f}s elapsed]", flush=True)

    print(f"\nDONE: {total_written} instances -> {out_dir} "
          f"in {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
