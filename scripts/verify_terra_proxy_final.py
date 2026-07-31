#!/usr/bin/env python
"""Produce one reproducible audit verdict for every Terra proxy response.

The script deliberately ignores the many incremental ``verification*.jsonl``
files.  It derives the only scorable response path from the frozen instance
index and task id, extracts code from that response, and verifies it in a
fresh Python process.  The parent enforces a wall-clock deadline per task, so
one pathological candidate cannot stall the complete audit.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
RUN = Path(os.environ.get(
    "QENCODEBENCH_AUDIT_RUN",
    ROOT / "runs" / "e1_terra_subagent_proxy_480",
))
INSTANCES = ROOT / "data" / "frozen_v1" / "instances.jsonl"
SOLUTIONS = ROOT / "data" / "frozen_v1" / "solutions.jsonl"
MODEL = os.environ.get("QENCODEBENCH_AUDIT_MODEL", "terra-subagent-proxy")
METHOD = "subagent_proxy"


def load_frozen():
    instances = [json.loads(line) for line in INSTANCES.open()]
    solutions = [json.loads(line) for line in SOLUTIONS.open()]
    if len(instances) != 480 or len(solutions) != 480:
        raise RuntimeError("expected exactly 480 frozen instances and solutions")
    sol_by_id = {row["task_id"]: set(row["solutions"]) for row in solutions}
    return instances, sol_by_id


def canonical_path(index: int, task_id: str) -> Path:
    return RUN / "responses" / f"{index:03d}_{task_id}.md"


def infra_row(index: int, task_id: str, reason: str) -> dict:
    return {
        "instance_index": index, "task_id": task_id, "model": MODEL,
        "method": METHOD, "sample_idx": 0,
        "level_reached": "INFRA_TIMEOUT" if reason == "INFRA_TIMEOUT" else "INFRA_ERROR",
        "pass": {"L1": None, "L2": None, "L3": None, "L4": None},
        "fail_reason": reason, "mark_accuracy": None, "counterexamples": [],
        "n_qubits_used": None, "depth_transpiled": None,
        "verify_time_s": None, "raw_response_path": str(canonical_path(index, task_id).relative_to(RUN)),
        "audit_status": "infrastructure_failure",
    }


def is_verifier_infrastructure_failure(row: dict) -> bool:
    """Return whether a verifier result is non-scorable infrastructure output.

    Verifier 0.1.6 reports a crashed isolated L3 worker through the normal
    ``verify_sample`` result schema.  Older audits consequently marked those
    rows as verified model failures.  Recognize that sentinel explicitly so
    ``--retry-infra`` can recover them without retrying genuine candidate-code
    runtime errors from L2.
    """
    reason = row.get("fail_reason") or ""
    l3_worker_crash = reason.startswith("RUNTIME_ERROR: l3 worker crashed:")
    l2_openmp_crash = (
        reason.startswith("RUNTIME_ERROR: sandbox crashed:")
        and ("Can't open SHM" in reason or "OMP: Error" in reason)
    )
    return (
        row.get("audit_status") == "infrastructure_failure"
        or l3_worker_crash
        or l2_openmp_crash
    )


def one(index: int) -> dict:
    """Run in an isolated process and print exactly one JSON object."""
    # Imports are intentionally delayed: this process is also the timeout
    # boundary around Qiskit/aer/verifier work.
    from qencodebench.core.task import TaskInstance
    from qencodebench.pipeline.extract import extract_code
    from qencodebench.verifier import verify_sample

    instances, sol_by_id = load_frozen()
    raw = instances[index]
    task_id = raw["task_id"]
    path = canonical_path(index, task_id)
    if not path.is_file():
        return infra_row(index, task_id, "MISSING_CANONICAL_RESPONSE")
    text = path.read_text(errors="replace")
    code = extract_code(text)
    row = verify_sample(code, TaskInstance.from_dict(raw), sol_by_id[task_id],
                        model=MODEL, method=METHOD, sample_idx=0)
    row["instance_index"] = index
    row["raw_response_path"] = str(path.relative_to(RUN))
    row["audit_status"] = (
        "infrastructure_failure"
        if is_verifier_infrastructure_failure(row)
        else "verified"
    )
    return row


def run_all(jobs: int, timeout_s: int, output: Path, retry_infra: Path | None = None) -> int:
    instances, _ = load_frozen()
    all_expected = [(i, row["task_id"]) for i, row in enumerate(instances)]
    retained: dict[int, dict] = {}
    if retry_infra is not None:
        old = [json.loads(line) for line in retry_infra.open()]
        if len(old) != 480 or {r.get("instance_index") for r in old} != set(range(480)):
            raise RuntimeError("retry source is not a 480-row canonical audit")
        retained = {
            r["instance_index"]: r
            for r in old
            if r.get("audit_status") == "verified"
            and not is_verifier_infrastructure_failure(r)
        }
    expected = [(i, task_id) for i, task_id in all_expected if i not in retained]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env["OMP_NUM_THREADS"] = "1"
    env["OPENBLAS_NUM_THREADS"] = "1"
    env["MKL_NUM_THREADS"] = "1"
    env["KMP_USE_SHM"] = "0"

    pending = iter(expected)
    active: dict[int, tuple[subprocess.Popen, float, str]] = {}
    rows: dict[int, dict] = dict(retained)
    while len(rows) < 480:
        while len(active) < jobs:
            try:
                index, task_id = next(pending)
            except StopIteration:
                break
            proc = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--one", str(index)],
                                    cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True)
            active[index] = (proc, time.monotonic(), task_id)
        progressed = False
        for index, (proc, started, task_id) in list(active.items()):
            if proc.poll() is None and time.monotonic() - started < timeout_s:
                continue
            progressed = True
            if proc.poll() is None:
                proc.kill()
                proc.communicate()
                rows[index] = infra_row(index, task_id, "INFRA_TIMEOUT")
            else:
                stdout, stderr = proc.communicate()
                try:
                    row = json.loads(stdout.strip().splitlines()[-1])
                    if row.get("instance_index") != index or row.get("task_id") != task_id:
                        raise ValueError("child identity mismatch")
                    rows[index] = row
                except (IndexError, json.JSONDecodeError, ValueError) as exc:
                    rows[index] = infra_row(index, task_id, f"INFRA_ERROR: {type(exc).__name__}: {stderr[-300:]}")
            del active[index]
            print(f"[{len(rows):03d}/480] {index:03d} {task_id}", flush=True)
        if not progressed:
            time.sleep(0.05)

    tmp = output.with_suffix(output.suffix + ".tmp")
    with tmp.open("w") as fh:
        for index, _ in all_expected:
            fh.write(json.dumps(rows[index], sort_keys=True) + "\n")
    tmp.replace(output)

    audited = [r for r in rows.values() if r["audit_status"] == "verified"]
    n_infra = 480 - len(audited)
    print("FINAL", json.dumps({
        "total": 480, "verified": len(audited),
        "infra": n_infra,
        **{level: {"pass": sum(r["pass"][level] is True for r in audited),
                    "denominator": sum(r["pass"][level] is not None for r in audited)}
           for level in ("L1", "L2", "L3", "L4")},
        "l4_end_to_end": sum(r["pass"]["L4"] is True for r in audited),
    }, sort_keys=True))
    return 0 if n_infra == 0 else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--one", type=int, help="verify one zero-based frozen index")
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--output", type=Path, default=RUN / "verification_final_canonical.jsonl")
    parser.add_argument("--retry-infra", type=Path,
                        help="reuse verified rows from a prior canonical audit and rerun only infra rows")
    args = parser.parse_args()
    if args.one is not None:
        print(json.dumps(one(args.one), sort_keys=True))
        return 0
    return run_all(max(1, args.jobs), max(1, args.timeout), args.output, args.retry_infra)


if __name__ == "__main__":
    raise SystemExit(main())
