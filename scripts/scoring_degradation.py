#!/usr/bin/env python
"""Scoring-regime degradation experiment (paper section: How Much Do
Sampled Tests Overestimate?).

Re-scores every direct-generation sample under three degraded regimes
and compares against the stored complete-verification (L3) ground truth:

  basis-16 / basis-64 : k random basis-state input--output checks, the
      analogue of end-to-end test suites in prior quantum benchmarks.
      A phase oracle acts as the identity on basis states, so phase
      errors are invisible here by construction.
  super-4 : a stronger degraded baseline -- 4 random product-state
      probes compared against the ideal oracle's output state (fidelity
      >= 1 - TOL, global phase automatically modded out).

Per-task test suites are seeded by task_id (a benchmark would ship a
fixed suite). Only samples that build (L2 pass) are re-scored; samples
that fail to build fail under every regime and carry no information
about scoring quality.

Metrics per configuration x regime: degraded pass@1, inflation vs L3 pass@1,
false-positive rate among accepted (AlphaCode convention), and the
cross-configuration ranking under each regime.

Outputs: analysis/scoring_degradation.jsonl (per sample) and
analysis/scoring_degradation.md (summary).
"""

from __future__ import annotations

import collections
import hashlib
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qencodebench.core.task import TaskInstance

ARMS = [
    ("qwen2.5-7b (greedy)", "e1_c_group_greedy"),
    ("deepseek-v4-flash (t=0.7)", "e1_b_deepseek"),
    ("deepseek-v4-flash + thinking", "e1_b_ds_thinking"),
]
K_BASIS = (16, 64)
K_SUPER = 4
TOL = 0.99
WORKERS = 10

_INSTANCES: dict = {}
_SOLUTIONS: dict = {}


def _load_frozen():
    for line in open("data/frozen_v1/instances.jsonl"):
        d = json.loads(line)
        _INSTANCES[d["task_id"]] = TaskInstance.from_dict(d)
    for line in open("data/frozen_v1/solutions.jsonl"):
        d = json.loads(line)
        _SOLUTIONS[d["task_id"]] = set(d["solutions"])


def _task_seed(task_id: str) -> int:
    return int(hashlib.sha256(task_id.encode()).hexdigest()[:8], 16)


def score_sample(job):
    """(task_id, code) -> dict of degraded verdicts, or None on no-build."""
    task_id, code = job
    from qencodebench.verifier.verify import sandbox_build
    from qencodebench.core.sim import run_statevector
    from qiskit import QuantumCircuit

    inst = _INSTANCES[task_id]
    sols = _SOLUTIONS[task_id]
    n = inst.n_problem_qubits
    circ, err = sandbox_build(code, n, inst.max_total_qubits)
    if circ is None:
        return None
    q = circ.num_qubits
    a = q - n
    dim = 1 << n
    rng = np.random.default_rng(_task_seed(task_id))

    # ---- basis-state I/O tests ------------------------------------------
    xs = rng.choice(dim, size=min(max(K_BASIS), dim), replace=False)
    basis_ok = []
    for x in xs:
        prep = QuantumCircuit(q)
        for i in range(n):
            if (int(x) >> i) & 1:
                prep.x(i)
        prep.compose(circ, inplace=True)
        try:
            sv = run_statevector(prep)
        except Exception:
            return {"task_id": task_id, "built": True, "sim_error": True}
        basis_ok.append(abs(sv[int(x)]) ** 2 >= TOL)
    verdicts = {f"basis{k}": all(basis_ok[:k]) for k in K_BASIS}

    # ---- random product-state probes ------------------------------------
    sup_ok = []
    for _ in range(K_SUPER):
        thetas = rng.uniform(0, np.pi, size=n)
        phis = rng.uniform(0, 2 * np.pi, size=n)
        prep = QuantumCircuit(q)
        for i in range(n):
            prep.ry(thetas[i], i)
            prep.rz(phis[i], i)
        # ideal output amplitudes on the |x, 0^a> block
        amps = np.ones(1, dtype=complex)
        for i in range(n):
            one = np.array([np.cos(thetas[i] / 2),
                            np.exp(1j * phis[i]) * np.sin(thetas[i] / 2)])
            amps = (amps[None, :] * one[:, None]).reshape(-1)  # little-endian
        ideal = amps.copy()
        for s in sols:
            ideal[s] *= -1.0
        prep.compose(circ, inplace=True)
        try:
            sv = run_statevector(prep)
        except Exception:
            return {"task_id": task_id, "built": True, "sim_error": True}
        block = sv[:dim]
        fid = abs(np.vdot(ideal, block)) ** 2
        sup_ok.append(fid >= TOL)
    verdicts[f"super{K_SUPER}"] = all(sup_ok)
    verdicts.update({"task_id": task_id, "built": True, "sim_error": False})
    return verdicts


def main() -> int:
    _load_frozen()
    os.makedirs("analysis", exist_ok=True)
    out_rows = open("analysis/scoring_degradation.jsonl", "w")
    summary = {}
    for arm_name, run in ARMS:
        truth = {}
        built_l2 = {}
        for line in open(f"runs/{run}/verify_results.jsonl"):
            r = json.loads(line)
            key = (r["task_id"], r["sample_idx"])
            truth[key] = bool(r["pass"]["L3"])
            built_l2[key] = bool(r["pass"].get("L2"))
        codes = {}
        for line in open(f"runs/{run}/raw_responses.jsonl"):
            d = json.loads(line)
            key = (d["task_id"], d["sample_idx"])
            if d.get("extracted_code"):
                codes[key] = d["extracted_code"]
        jobs, keys = [], []
        for key, ok2 in built_l2.items():
            if ok2 and key in codes:
                jobs.append((key[0], codes[key]))
                keys.append(key)
        print(f"{arm_name}: {len(truth)} samples, {len(jobs)} buildable",
              flush=True)
        # macOS spawn: workers re-import the module with empty globals,
        # so each worker loads the frozen set itself via the initializer
        with Pool(WORKERS, initializer=_load_frozen) as pool:
            results = pool.map(score_sample, jobs, chunksize=4)

        regimes = [f"basis{k}" for k in K_BASIS] + [f"super{K_SUPER}"]
        # per-sample verdicts: unbuildable/sim-error samples fail everywhere
        per_task = collections.defaultdict(
            lambda: {r: [] for r in regimes + ["L3"]})
        for key in truth:
            per_task[key[0]]["L3"].append(truth[key])
        for key, res in zip(keys, results):
            for r in regimes:
                v = bool(res and not res.get("sim_error") and res.get(r))
                per_task[key[0]][r].append((v, truth[key]))
        # tasks with no buildable sample contribute all-False degraded rows
        arm_stats = {}
        for r in regimes:
            acc_wrong = acc_total = 0
            task_rates = []
            for tid, d in per_task.items():
                pairs = d[r]
                n_samp = len(d["L3"])
                passed = sum(1 for v, _ in pairs if v)
                acc_total += passed
                acc_wrong += sum(1 for v, t in pairs if v and not t)
                task_rates.append(passed / n_samp)
            p1 = float(np.mean(task_rates))
            l3_p1 = float(np.mean(
                [np.mean(d["L3"]) for d in per_task.values()]))
            arm_stats[r] = dict(
                degraded_pass1=p1, l3_pass1=l3_p1,
                inflation_pp=100 * (p1 - l3_p1),
                fp_rate=(acc_wrong / acc_total) if acc_total else 0.0,
                accepted=acc_total, accepted_wrong=acc_wrong)
            out_rows.write(json.dumps(
                {"config": arm_name, "regime": r, **arm_stats[r]}) + "\n")
        summary[arm_name] = arm_stats
        print(json.dumps({arm_name: arm_stats}, indent=1), flush=True)

    # ---- markdown summary -------------------------------------------------
    regimes = [f"basis{k}" for k in K_BASIS] + [f"super{K_SUPER}"]
    lines = ["# Scoring-regime degradation (direct rows, frozen core set)",
             "", "| config | regime | degraded pass@1 | L3 pass@1 | "
             "inflation (pp) | FP rate among accepted |", "|" + "---|" * 6]
    for arm_name, st in summary.items():
        for r in regimes:
            s = st[r]
            lines.append(
                f"| {arm_name} | {r} | {100*s['degraded_pass1']:.1f} | "
                f"{100*s['l3_pass1']:.1f} | {s['inflation_pp']:+.1f} | "
                f"{100*s['fp_rate']:.1f}% ({s['accepted_wrong']}/"
                f"{s['accepted']}) |")
    lines.append("")
    lines.append("Ranking check: order of the three configurations under each regime "
                 "vs under L3.")
    for r in regimes + ["L3"]:
        if r == "L3":
            order = sorted(summary, key=lambda a: -summary[a]["basis16"]["l3_pass1"])
        else:
            order = sorted(summary, key=lambda a: -summary[a][r]["degraded_pass1"])
        lines.append(f"- {r}: " + " > ".join(order))
    with open("analysis/scoring_degradation.md", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    out_rows.close()
    print("DONE -> analysis/scoring_degradation.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
