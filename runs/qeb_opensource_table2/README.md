# QEncodeBench — open-weight Table 2 (direct generation)

Direct-generation results for eight open-weight configurations on the
QEncodeBench core set (`frozen_v1.0`, 480 instances), scored by the project
verifier: L1 syntax → L2 sandboxed build → L3 full solution-set
semantic equivalence (the primary metric) → L4 resource budgets. Method =
`direct`, one attempt per instance (`n=1`). Non-reasoning models decode greedily
(temp 0); reasoning models use each model card's recommended thinking-mode
sampling (temp 0.6 for Qwen3 / DeepSeek-R1, temp 1.0 for gpt-oss).

## Results (L3 = semantic pass@1, %)

| Model | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| Qwen2.5-Coder-7B-Instruct | 100.0 | 46.9 | 0.0 | 0.0 |
| Qwen2.5-Coder-32B-Instruct | 100.0 | 43.1 | 0.2 | 0.2 |
| Qwen3-32B (thinking off) | 99.8 | 44.6 | 1.9 | 1.9 |
| DeepSeek-R1-0528-Qwen3-8B | 86.0 | 16.7 | 1.0 | 0.8 |
| Qwen3-32B (thinking on) | 99.8 | 58.3 | 20.4 | 19.8 |
| Qwen3-235B-A22B-Thinking-2507 | 99.8 | 56.9 | 34.2 | 31.9 |
| gpt-oss-20b (reasoning high) | 90.0 | 74.4 | 68.8 | 60.4 |
| gpt-oss-120b (reasoning high) | 97.7 | 94.2 | 81.2 | 69.0 |

Full per-family and per-tier breakdowns are in `table2_final.csv`;
a rendered version is `table2_final.md`.

Reading: non-reasoning coders sit at the floor (≈0%); enabling thinking on the
same Qwen3-32B weights lifts L3 from 1.9 to 20.4; scale within Qwen3 helps
(32B→235B, 20.4→34.2); the gpt-oss models lead by a wide margin and are the only
configurations to make non-trivial progress on 3-coloring and vertex cover.

## Weights and serving

All models served with vLLM 0.24.0 (OpenAI-compatible endpoint), one instance
per model. Qwen2.5-Coder-32B, Qwen3-32B and Qwen3-235B use AWQ int4;
DeepSeek-R1-0528-Qwen3-8B is bf16; gpt-oss-20b/120b are MXFP4. Per-run
settings (model tag, max_tokens, sampling) are recorded in each run's
`config_snapshot.yaml`; the two merged gpt-oss rows carry no single snapshot —
their budget-round components are under `runs_provenance/`.

## Files

```
table2_final.md / .csv                      the table above + family/tier breakdowns
token_budget_truncation.md                  budget-truncation methodology note
runs/<config>/
    verify_results.jsonl   one row per instance: pass{L1..L4}, fail_reason,
                           mark_accuracy, counterexamples, n_qubits_used,
                           depth_transpiled, verifier_version
    raw_responses.jsonl    one row per instance: response_text, extracted_code,
                           tokens_in/out, prompt_sha256
    config_snapshot.yaml   the run configuration (absent for the two
                           merged gpt-oss rows; see runs_provenance/)
runs_provenance/            gpt-oss budget-round components (see note below)
```

## gpt-oss budget handling (read before comparing gpt-oss rows)

High-effort gpt-oss emits very long chain-of-thought. At a 32k output cap it is
truncated before emitting an answer (65% of gpt-oss-20b, 18% of gpt-oss-120b),
which understates L3. Each truncated/timed-out instance was re-run at a larger
budget (up to 90k) and the highest-budget passing attempt kept per instance; the
`runs/gptoss20b_final` and `runs/gptoss120b_final` rows are these merges, and the
budget-round components are in `runs_provenance/`. A residual 8.3% of the hardest
instances never terminate even at 90k (the model keeps reasoning past the cap);
these are counted as failures. Details and per-model truncation rates are in
`token_budget_truncation.md`.

## Notes

- 3840 verified instances across the eight configurations (plus the
  provenance re-runs), all scored by the same verifier.
- Bit i of an assignment lives on `problem_qubits[i]` (little-endian);
  correctness is modulo a global phase; F2/F5 use the surjective 2-bit colour
  code (11→0), as spelled out in every problem statement.
