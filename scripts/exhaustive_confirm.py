#!/usr/bin/env python
"""Exhaustively confirm every L3-accepted pipeline-run sample.

For each run with (verify_results.jsonl, raw_responses.jsonl,
config_snapshot.yaml), every row with pass.L3 == true is re-verified from
its stored extracted_code with the exhaustive per-basis check FORCED after
the fast path.  Existing run artifacts are never modified; results go to
runs/exhaustive_confirmation/<run>.confirm.jsonl (resumable).

A row is a "flip" when the forced re-verification does not reproduce the
accepted L3 verdict (either the fast path itself, or the exhaustive
confirmation raising VerifierInconsistency).
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import subprocess
import sys
import tempfile
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
# candidate code may import qencodebench (unit-agent assembly library); the
# sandbox child processes must inherit the package path like the original
# pipeline runs did
os.environ["PYTHONPATH"] = _ROOT + (
    os.pathsep + os.environ["PYTHONPATH"]
    if os.environ.get("PYTHONPATH") else "")

KEY = ("task_id", "model", "method", "sample_idx", "prompt_variant")
OUT_DIR = "runs/exhaustive_confirmation"
SKIP_RUNS = set()

_INSTS, _SOLS = {}, {}
_LAST = {"method": None, "affordable": None}


def _patch_verifier():
    """Force the exhaustive confirmation on both L3 execution paths and
    record which path produced the verdict."""
    import qencodebench.verifier.verify as V
    from qencodebench.verifier.functional import MAX_DIAG_CIRCUIT_SIZE
    from qiskit import qpy

    def forced_verify_functional(circ, inst, solutions, sample_key="0"):
        _LAST["affordable"] = (
            circ.size() <= MAX_DIAG_CIRCUIT_SIZE
            and (1 << inst.n_problem_qubits) * max(circ.size(), 1) <= 5e8)
        if not V._simulation_risk(circ):
            res = V.verify_circuit(circ, inst.n_problem_qubits, inst.task_id,
                                   solutions, sample_key=sample_key,
                                   force_exhaustive=True)
            _LAST["method"] = res.method
            return res
        with tempfile.TemporaryDirectory() as tmp:
            qpy_path = os.path.join(tmp, "cand.qpy")
            with open(qpy_path, "wb") as fh:
                qpy.dump(circ, fh)
            job = json.dumps({
                "qpy_path": qpy_path, "n_problem": inst.n_problem_qubits,
                "task_id": inst.task_id, "solutions": sorted(solutions),
                "sample_key": sample_key, "force_exhaustive": True,
            })
            runner = os.path.join(os.path.dirname(V.__file__),
                                  "_l3_runner.py")
            try:
                proc = subprocess.run([sys.executable, runner], input=job,
                                      capture_output=True, text=True,
                                      timeout=V.L3_TIMEOUT_S)
            except subprocess.TimeoutExpired:
                _LAST["method"] = "A-isolated-timeout"
                return V.FuncResult(False, "TIMEOUT", None, [], "A-isolated")
            for line in proc.stdout.splitlines():
                if line.startswith("QEB_L3_FREEZE:"):
                    raise V.VerifierInconsistency(
                        line[len("QEB_L3_FREEZE:"):])
                if line.startswith("QEB_L3:"):
                    d = json.loads(line[len("QEB_L3:"):])
                    r = V.FuncResult(**d)
                    _LAST["method"] = r.method
                    return r
            _LAST["method"] = "A-isolated-crash"
            return V.FuncResult(
                False, f"RUNTIME_ERROR: l3 worker crashed: "
                       f"{proc.stderr[-300:]}", None, [], "A-isolated")

    V.verify_functional = forced_verify_functional


def _init_worker(cfg_path: str):
    import yaml
    from qencodebench.core.task import TaskInstance
    _patch_verifier()
    cfg = yaml.safe_load(open(cfg_path))
    for line in open(cfg["instances_path"]):
        d = json.loads(line)
        _INSTS[d["task_id"]] = TaskInstance.from_dict(d)
    for line in open(cfg["solutions_path"]):
        d = json.loads(line)
        _SOLS[d["task_id"]] = set(d["solutions"])


def _confirm_one(job):
    key, code = job
    from qencodebench.verifier import verify_sample
    from qencodebench.verifier.verify import VerifierInconsistency
    _LAST["method"] = _LAST["affordable"] = None
    t0 = time.time()
    task_id = key[0]
    try:
        row = verify_sample(code, _INSTS[task_id], _SOLS[task_id],
                            model=key[1], method=key[2], sample_idx=key[3])
        new_l3 = bool(row["pass"]["L3"])
        detail = row["fail_reason"]
    except VerifierInconsistency as e:
        new_l3, detail = False, f"EXHAUSTIVE_FLIP: {e}"
    return {"key": list(key), "new_L3": new_l3,
            "verifier_method": _LAST["method"],
            "exhaustive_affordable": _LAST["affordable"],
            "detail": detail, "time_s": round(time.time() - t0, 2)}


def confirm_run(run: str, workers: int) -> tuple[int, int, int]:
    vr = f"runs/{run}/verify_results.jsonl"
    accepted = {}
    for line in open(vr):
        d = json.loads(line)
        if d["pass"]["L3"]:
            accepted[tuple(d.get(k) for k in KEY)] = d
    out_path = f"{OUT_DIR}/{run}.confirm.jsonl"
    done = set()
    if os.path.exists(out_path):
        for line in open(out_path):
            done.add(tuple(json.loads(line)["key"]))
    todo_keys = [k for k in accepted if k not in done]
    if not todo_keys:
        return len(accepted), 0, 0
    raw = {}
    for line in open(f"runs/{run}/raw_responses.jsonl"):
        d = json.loads(line)
        raw[tuple(d.get(k) for k in KEY)] = d.get("extracted_code")
    jobs, missing = [], 0
    for k in todo_keys:
        code = raw.get(k)
        if code:
            jobs.append((k, code))
        else:
            missing += 1
    flips = 0
    cfg = f"runs/{run}/config_snapshot.yaml"
    with mp.get_context("spawn").Pool(workers, _init_worker, (cfg,)) as pool, \
            open(out_path, "a") as fh:
        for res in pool.imap_unordered(_confirm_one, jobs, chunksize=4):
            if not res["new_L3"]:
                flips += 1
                print(f"  FLIP {run} {res['key']}: {res['detail']}",
                      flush=True)
            fh.write(json.dumps(res) + "\n")
            fh.flush()
    return len(accepted), flips, missing


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--runs", nargs="*", default=None)
    args = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    runs = args.runs or sorted(
        os.path.basename(os.path.dirname(p))
        for p in __import__("glob").glob("runs/*/verify_results.jsonl"))
    grand_acc = grand_flips = grand_missing = 0
    for run in runs:
        if run in SKIP_RUNS:
            continue
        if not os.path.exists(f"runs/{run}/config_snapshot.yaml"):
            print(f"{run}: no config snapshot, SKIPPED", flush=True)
            continue
        t0 = time.time()
        acc, flips, missing = confirm_run(run, args.workers)
        grand_acc += acc
        grand_flips += flips
        grand_missing += missing
        print(f"{run}: {acc} accepted, {flips} flips, {missing} missing-code "
              f"({time.time()-t0:.0f}s)", flush=True)
    print(f"\nTOTAL accepted={grand_acc} flips={grand_flips} "
          f"missing_code={grand_missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
