#!/usr/bin/env python
"""Retry timed-out exhaustive-confirmation rows with a long timeout.

Appends fresh verdicts to the same confirm files; aggregation is
last-record-wins per key.
"""

from __future__ import annotations

import glob
import json
import multiprocessing as mp
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
os.environ["PYTHONPATH"] = _ROOT + (
    os.pathsep + os.environ["PYTHONPATH"]
    if os.environ.get("PYTHONPATH") else "")

from scripts.exhaustive_confirm import (  # noqa: E402
    KEY, _confirm_one, _init_worker)


def _init_worker_long(cfg_path: str):
    _init_worker(cfg_path)
    import qencodebench.verifier.verify as V
    V.L3_TIMEOUT_S = 3600


def main() -> int:
    for path in sorted(glob.glob("runs/exhaustive_confirmation/*.confirm.jsonl")):
        run = os.path.basename(path)[:-len(".confirm.jsonl")]
        last = {}
        for line in open(path):
            d = json.loads(line)
            last[tuple(d["key"])] = d
        failed = [k for k, d in last.items() if not d["new_L3"]]
        if not failed:
            continue
        raw = {}
        for line in open(f"runs/{run}/raw_responses.jsonl"):
            d = json.loads(line)
            raw[tuple(d.get(k) for k in KEY)] = d.get("extracted_code")
        jobs = [(k, raw[k]) for k in failed if raw.get(k)]
        cfg = f"runs/{run}/config_snapshot.yaml"
        n_pass = 0
        with mp.get_context("spawn").Pool(
                min(6, len(jobs)), _init_worker_long, (cfg,)) as pool, \
                open(path, "a") as fh:
            for res in pool.imap_unordered(_confirm_one, jobs):
                res["retry"] = True
                n_pass += bool(res["new_L3"])
                fh.write(json.dumps(res) + "\n")
                fh.flush()
                if not res["new_L3"]:
                    print(f"  STILL-FAILING {run} {res['key']}: "
                          f"{str(res['detail'])[:120]}", flush=True)
        print(f"{run}: {len(jobs)} retried, {n_pass} now pass", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
