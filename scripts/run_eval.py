#!/usr/bin/env python
"""Run an evaluation: generation pass (LLM queries, resumable) followed by
the verification pass.

Usage:
    python scripts/run_eval.py --config configs/runs/e1_b_deepseek.yaml
    python scripts/run_eval.py --config ... --verify-only
"""

from __future__ import annotations

import argparse
import os

from qencodebench.pipeline.runner import (
    RunConfig, run_generation, run_verification,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--verify-only", action="store_true")
    ap.add_argument("--generate-only", action="store_true")
    args = ap.parse_args()

    cfg = RunConfig.from_yaml(args.config)
    run_dir = os.path.join(cfg.runs_dir, cfg.run_id)
    if not args.verify_only:
        run_dir = run_generation(cfg)
    if not args.generate_only:
        run_verification(run_dir, cfg.instances_path, cfg.solutions_path)


if __name__ == "__main__":
    main()
