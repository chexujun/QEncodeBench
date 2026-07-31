# claude_full480 — Claude runs on the 480-instance core set

Claude Opus 4.8 and Claude Haiku 4.5 on the complete core set
(`data/frozen_v1/`, 480 instances) for the build-oracle task. Each
instance is a one-shot generation (n=1): the model receives the
frozen verbose prompt for one instance and returns a single
`build_oracle` code block, with no execution, testing, or iteration.

The raw generated code is under `code/<tag>_480/<task_id>.py`
(480 files per model). Every file is scored by the repository
verifier — the same L1→L2→L3→L4 gates used for every other row —
producing `<tag>_480_verify.jsonl` (full `verify_sample` schema:
`level_reached`, `verify_time_s`, `mark_accuracy`,
`counterexamples`, and the ref fields). Results are in `table.md`;
these are the paper's Claude rows.

## Usage caveats (read before citing)

1. **Protocol**: these runs were executed under an agent harness
   whose system prompt differs from a raw API call; they are not
   directly comparable to the open-weight rows and are marked
   accordingly in the paper.
2. Generation-side metadata (sampling parameters, per-instance
   prompt hashes, timestamps, API-echoed model id) was not retained
   by the harness.

## Files

```
code/opus_480/<task_id>.py    raw generated code, one file per instance
code/haiku_480/<task_id>.py
opus_480_verify.jsonl         480 scored rows, full local schema
haiku_480_verify.jsonl
table.md                      summary table (L1–L4 + families + tiers)
```

Scoring logic: for each instance, read the code file, then
`verify_sample(code, instance, solutions)` (L1 syntax/API ban →
L2 sandboxed build → L3 full solution-set equivalence → L4
transpiled depth and qubit budgets), with instances and golden
solution sets from `data/frozen_v1/`.
