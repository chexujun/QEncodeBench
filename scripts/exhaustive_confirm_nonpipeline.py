#!/usr/bin/env python
"""Exhaustively confirm L3-accepted rows stored outside the standard
pipeline layout.

Groups
  os_<run>   : runs/qeb_opensource_table2/runs/<run>/
               (standard raw_responses/verify_results schema)
  claude     : accepted set from runs/claude_full480/*_verify.jsonl,
               code from runs/claude_full480/code/<tag>_480/<task_id>.py
  terra (e1) : accepted set from verification_final_canonical_corrected.jsonl,
               code extracted from the canonical response markdown

All instances are frozen_v1.  Results are appended to
runs/exhaustive_confirmation/<name>.confirm.jsonl (resumable,
last record per key wins).
"""

from __future__ import annotations

import json
import multiprocessing as mp
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
os.environ["PYTHONPATH"] = _ROOT + (
    os.pathsep + os.environ["PYTHONPATH"]
    if os.environ.get("PYTHONPATH") else "")

from scripts.exhaustive_confirm import _patch_verifier, _INSTS, _SOLS  # noqa: E402

OUT_DIR = "runs/exhaustive_confirmation"


def _init_frozen():
    from qencodebench.core.task import TaskInstance
    import qencodebench.verifier.verify as V
    _patch_verifier()
    V.L3_TIMEOUT_S = 3600
    for line in open("data/frozen_v1/instances.jsonl"):
        d = json.loads(line)
        _INSTS[d["task_id"]] = TaskInstance.from_dict(d)
    for line in open("data/frozen_v1/solutions.jsonl"):
        d = json.loads(line)
        _SOLS[d["task_id"]] = set(d["solutions"])


def _confirm_one(job):
    from scripts.exhaustive_confirm import _confirm_one as inner
    return inner(job)


def _drain(name: str, jobs, workers=6):
    out = f"{OUT_DIR}/{name}.confirm.jsonl"
    done = set()
    if os.path.exists(out):
        for line in open(out):
            done.add(tuple(json.loads(line)["key"]))
    jobs = [(k, c) for k, c in jobs if tuple(k) not in done]
    if not jobs:
        print(f"{name}: nothing to do", flush=True)
        return
    flips = 0
    with mp.get_context("spawn").Pool(workers, _init_frozen) as pool, \
            open(out, "a") as fh:
        for res in pool.imap_unordered(_confirm_one, jobs, chunksize=2):
            if not res["new_L3"]:
                flips += 1
                print(f"  NON-PASS {name} {res['key']}: "
                      f"{str(res['detail'])[:100]}", flush=True)
            fh.write(json.dumps(res) + "\n")
            fh.flush()
    print(f"{name}: {len(jobs)} confirmed, {flips} non-pass", flush=True)


def opensource_jobs(run: str):
    base = f"runs/qeb_opensource_table2/runs/{run}"
    keyf = ("task_id", "model", "method", "sample_idx")
    accepted = set()
    for line in open(f"{base}/verify_results.jsonl"):
        d = json.loads(line)
        if d["pass"]["L3"]:
            accepted.add(tuple(d.get(k) for k in keyf))
    for line in open(f"{base}/raw_responses.jsonl"):
        d = json.loads(line)
        k = tuple(d.get(kk) for kk in keyf)
        if k in accepted and d.get("extracted_code"):
            yield list(k) + ["verbose"], d["extracted_code"]


def claude_jobs(tag: str):
    for line in open(f"runs/claude_full480/{tag}_480_verify.jsonl"):
        d = json.loads(line)
        if not d["pass"]["L3"]:
            continue
        code = open(f"runs/claude_full480/code/{tag}_480/"
                    f"{d['task_id']}.py").read()
        yield [d["task_id"], d["model"], "claude_code", 0, "verbose"], code


def terra_jobs():
    from qencodebench.pipeline.extract import extract_code
    run = "runs/e1_terra_subagent_proxy_480"
    for line in open(f"{run}/verification_final_canonical_corrected.jsonl"):
        d = json.loads(line)
        if not d["pass"]["L3"]:
            continue
        path = os.path.join(run, d["raw_response_path"])
        code = extract_code(open(path, errors="replace").read())
        if code:
            yield [d["task_id"], d["model"], d["method"], 0, "verbose"], code


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    for run in sorted(os.listdir("runs/qeb_opensource_table2/runs")):
        _drain(f"os_{run}", list(opensource_jobs(run)))
    for tag in ("opus", "haiku"):
        _drain(f"claude_{tag}", list(claude_jobs(tag)))
    _drain("e1_terra_subagent_proxy_480", list(terra_jobs()))
    print("CONFIRMATION COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
