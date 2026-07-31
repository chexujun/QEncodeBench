# Terra subagent proxy — canonical verbose rerun

This directory is a new run. It does not reuse responses from any earlier run.

Qualification contract:

1. Each frozen instance is rendered with `build_prompt(inst, "verbose")`.
2. Every exact payload is stored in `prompts/` and hashed in `prompt_manifest.jsonl`.
3. The solver message is byte-identical to that stored verbose prompt; no scheduler wrapper may alter it.
4. The prompt import convention (`qiskit`, `numpy`, `math`) is recorded per task.
5. `qualification_report.json` establishes the prepared-input qualification.
   Dispatch qualification is established during scheduling by hashing and
   directly embedding each full prompt as the sole initial solver message.

The run is complete. See `STATUS.md` for the delivered L1-L4 results and
`verification_final_canonical_retry.jsonl` for the merged, zero-infrastructure-
failure verification record. Our independent full re-verification is
`audit_reverify.jsonl`; it is the verification of record for the paper
(three delivered TIMEOUT verdicts pass under the forced exhaustive stage).
