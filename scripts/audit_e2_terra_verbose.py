#!/usr/bin/env python
"""Independent audit of runs/e2_terra_subagent_proxy_verbose_480.

Every canonical response is re-verified from scratch in our own
environment (extractor + verifier), with the exhaustive per-basis stage
forced on every fast-path acceptance, so the output doubles as the
A-route confirmation record. Results go to
runs/e2_terra_subagent_proxy_verbose_480/audit_reverify.jsonl
(resumable); nothing in the delivered run directory is modified.
"""

from __future__ import annotations

import json
import multiprocessing as mp
import os
import sys
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
os.environ["PYTHONPATH"] = _ROOT + (
    os.pathsep + os.environ["PYTHONPATH"]
    if os.environ.get("PYTHONPATH") else "")

RUN = "runs/e2_terra_subagent_proxy_verbose_480"
OUT = f"{RUN}/audit_reverify.jsonl"

_INSTS, _SOLS = {}, {}


def _init_worker():
    from qencodebench.core.task import TaskInstance
    from scripts.exhaustive_confirm import _patch_verifier
    import qencodebench.verifier.verify as V
    _patch_verifier()
    V.L3_TIMEOUT_S = 3600
    for line in open("data/frozen_v1/instances.jsonl"):
        d = json.loads(line)
        _INSTS[d["task_id"]] = TaskInstance.from_dict(d)
    for line in open("data/frozen_v1/solutions.jsonl"):
        d = json.loads(line)
        _SOLS[d["task_id"]] = set(d["solutions"])


def _one(job):
    idx, task_id = job
    from qencodebench.pipeline.extract import extract_code
    from qencodebench.verifier import verify_sample
    from qencodebench.verifier.verify import VerifierInconsistency
    t0 = time.time()
    path = f"{RUN}/responses/{idx:03d}_{task_id}.md"
    code = extract_code(open(path, errors="replace").read())
    try:
        row = verify_sample(code, _INSTS[task_id], _SOLS[task_id],
                            model="terra-subagent-proxy-verbose",
                            method="subagent_proxy")
    except VerifierInconsistency as e:
        row = {"task_id": task_id,
               "pass": {"L1": None, "L2": None, "L3": False, "L4": False},
               "fail_reason": f"EXHAUSTIVE_FLIP: {e}"}
    row["instance_index"] = idx
    row["audit_time_s"] = round(time.time() - t0, 2)
    return row


def main() -> int:
    insts = [json.loads(l) for l in open("data/frozen_v1/instances.jsonl")]
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            done.add(json.loads(line)["instance_index"])
    jobs = [(i, d["task_id"]) for i, d in enumerate(insts)
            if i not in done]
    print(f"{len(jobs)} to audit ({len(done)} already done)", flush=True)
    with mp.get_context("spawn").Pool(6, _init_worker) as pool, \
            open(OUT, "a") as fh:
        n = 0
        for row in pool.imap_unordered(_one, jobs, chunksize=2):
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            n += 1
            if n % 40 == 0:
                print(f"{n}/{len(jobs)} done", flush=True)
    print("AUDIT COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
