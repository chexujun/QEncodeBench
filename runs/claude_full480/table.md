# Claude full-480 results (L1–L4 %, by family, by graded tier)

| Model | L1 | L2 | L3 | L4 | SAT | Col. | VC | Sum | Latin | Match | T1 | T2 | T3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Claude Opus 4.8 | 99.8 | 90.2 | 65.2 | 59.0 | 61.0 | 49.0 | 67.1 | 58.6 | 77.1 | 87.1 | 72.6 | 64.6 | 58.2 |
| Claude Haiku 4.5 | 100.0 | 79.4 | 49.0 | 45.2 | 46.0 | 17.0 | 38.6 | 57.1 | 81.4 | 68.6 | 65.9 | 50.0 | 30.4 |

Computed by scoring the code files under `code/` with the repository
verifier; the per-sample rows are `opus_480_verify.jsonl` and
`haiku_480_verify.jsonl`. These are the paper's Claude rows.
