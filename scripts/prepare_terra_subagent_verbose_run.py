#!/usr/bin/env python
"""Prepare a fully auditable, canonical-verbose subagent evaluation run.

This script deliberately does no model generation.  It materializes the
exact ``build_prompt(instance, \"verbose\")`` payload for every frozen task,
records a SHA-256 for every payload, and writes the run-level parameters that
must be satisfied before fresh solver subagents are scheduled.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qencodebench.core.task import TaskInstance
from qencodebench.prompts import build_prompt, prompt_sha256


INSTANCES = ROOT / "data" / "frozen_v1" / "instances.jsonl"
DEFAULT_RUN = ROOT / "runs" / "e2_terra_subagent_proxy_verbose_480"
IMPORT_CONVENTION = {
    "allowed_import_roots": ["qiskit", "numpy", "math"],
    "source": "qencodebench.prompts.templates._VERBOSE_STATIC",
    "enforcement": (
        "Prompt contract only. The current verifier bans selected bypass "
        "APIs but does not implement a general import allowlist."
    ),
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def prepare(run: Path) -> None:
    if run.exists():
        raise RuntimeError(f"refusing to overwrite existing run directory: {run}")

    rows = [json.loads(line) for line in INSTANCES.read_text().splitlines()]
    if len(rows) != 480:
        raise RuntimeError(f"expected 480 frozen instances, found {len(rows)}")

    prompts = run / "prompts"
    responses = run / "responses"
    prompts.mkdir(parents=True)
    responses.mkdir()

    manifest: list[dict] = []
    for index, raw in enumerate(rows):
        inst = TaskInstance.from_dict(raw)
        prompt = build_prompt(inst, "verbose")
        digest = prompt_sha256(prompt)
        filename = f"{index:03d}_{inst.task_id}.txt"
        prompt_path = prompts / filename
        prompt_path.write_text(prompt)
        if sha256_file(prompt_path) != digest:
            raise RuntimeError(f"prompt hash mismatch after write: {index} {inst.task_id}")
        manifest.append({
            "instance_index": index,
            "task_id": inst.task_id,
            "family": inst.family,
            "tier": inst.tier,
            "seed": inst.seed,
            "prompt_variant": "verbose",
            "prompt_builder": "qencodebench.prompts.build_prompt",
            "prompt_path": f"prompts/{filename}",
            "prompt_sha256": digest,
            "prompt_bytes_utf8": len(prompt.encode("utf-8")),
            "solver_message_sha256": digest,
            "solver_message_mode": "exact_build_prompt_verbose",
            "n_problem_qubits": inst.n_problem_qubits,
            "max_total_qubits": inst.max_total_qubits,
            "max_depth": inst.max_depth,
            "import_convention": IMPORT_CONVENTION,
        })

    with (run / "prompt_manifest.jsonl").open("w") as fh:
        for row in manifest:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    run_parameters = {
        "schema_version": "1.0",
        "run_id": run.name,
        "method": "subagent_proxy",
        "prompt_variant": "verbose",
        "n_samples_per_instance": 1,
        "frozen_instances_path": "data/frozen_v1/instances.jsonl",
        "frozen_instances_sha256": sha256_file(INSTANCES),
        "prompt_builder": "qencodebench.prompts.build_prompt",
        "solver_message_mode": "exact_build_prompt_verbose",
        "solver_message_wrapper": None,
        "fresh_solver_per_instance": True,
        "fork_turns": "none",
        "canonical_response_pattern": "responses/{index:03d}_{task_id}.md",
        "solver_tool_policy": (
            "No additional tool-control text is appended, so the solver "
            "message remains byte-identical to build_prompt(..., 'verbose'). "
            "Platform-level tool availability is not auditable here."
        ),
        "model_profile": "Terra user-interface profile; exact model ID and reasoning parameters unavailable",
        "max_threads_configured": 20,
        "import_convention": IMPORT_CONVENTION,
    }
    write_json(run / "run_parameters.json", run_parameters)

    canonical = "# Canonical response identity\n\n"
    canonical += "The only scorable response for frozen instance i is:\n\n"
    canonical += "`responses/{i:03d}_{task_id}.md`\n\n"
    canonical += "Its solver message must be exactly the corresponding `prompts/` file. "
    canonical += "The SHA-256 is recorded in `prompt_manifest.jsonl`.\n"
    (run / "canonical_manifest.md").write_text(canonical)

    readme = "# Terra subagent proxy — canonical verbose rerun\n\n"
    readme += "This directory is a new run. It does not reuse responses from any earlier run.\n\n"
    readme += "Qualification contract:\n\n"
    readme += "1. Each frozen instance is rendered with `build_prompt(inst, \"verbose\")`.\n"
    readme += "2. Every exact payload is stored in `prompts/` and hashed in `prompt_manifest.jsonl`.\n"
    readme += "3. The solver message is byte-identical to that stored verbose prompt; no scheduler wrapper may alter it.\n"
    readme += "4. The prompt import convention (`qiskit`, `numpy`, `math`) is recorded per task.\n"
    readme += "5. Only after `qualification_report.json` passes may fresh solver responses be written to `responses/`.\n"
    (run / "README.md").write_text(readme)

    on_disk = [json.loads(line) for line in (run / "prompt_manifest.jsonl").read_text().splitlines()]
    checks = {
        "expected_instances": 480,
        "manifest_rows": len(on_disk),
        "unique_instance_indices": len({r["instance_index"] for r in on_disk}),
        "unique_task_ids": len({r["task_id"] for r in on_disk}),
        "unique_prompt_paths": len({r["prompt_path"] for r in on_disk}),
        "all_variant_verbose": all(r["prompt_variant"] == "verbose" for r in on_disk),
        "all_intended_solver_messages_exact": all(
            r["solver_message_mode"] == "exact_build_prompt_verbose"
            and r["solver_message_sha256"] == r["prompt_sha256"]
            for r in on_disk
        ),
        "all_prompt_hashes_match_files": all(
            sha256_file(run / r["prompt_path"]) == r["prompt_sha256"]
            for r in on_disk
        ),
        "all_import_conventions_recorded": all(
            r["import_convention"] == IMPORT_CONVENTION for r in on_disk
        ),
    }
    checks["input_qualified"] = (
        checks["manifest_rows"] == 480
        and checks["unique_instance_indices"] == 480
        and checks["unique_task_ids"] == 480
        and checks["unique_prompt_paths"] == 480
        and checks["all_variant_verbose"]
        and checks["all_intended_solver_messages_exact"]
        and checks["all_prompt_hashes_match_files"]
        and checks["all_import_conventions_recorded"]
    )
    # This preparation stage can prove the immutable input corpus only.  A
    # scheduler must separately record a hash of the message it actually
    # delivered to each solver before a generated response may be scored.
    checks["dispatch_qualified"] = False
    checks["dispatch_qualification_reason"] = (
        "Not established by preparation alone: actual solver-message bytes "
        "must be independently recorded and compared with prompt_sha256."
    )
    write_json(run / "qualification_report.json", checks)
    if not checks["input_qualified"]:
        raise RuntimeError(f"qualification failed: {checks}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    args = parser.parse_args()
    run = args.run_dir if args.run_dir.is_absolute() else ROOT / args.run_dir
    prepare(run)
    print(run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
