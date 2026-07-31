# Token-budget truncation in reasoning-model evaluation

## Summary

Reasoning models emit a long chain-of-thought before the final answer. When
that chain plus the answer exceeds the generation cap (`max_tokens`), the
response is cut off **during reasoning**, before any `build_oracle` code is
produced. The verifier then sees an empty / codeless response and fails it at
L1 (syntax). The reported semantic pass@1 (L3) for such a run is therefore a
**lower bound**: it conflates the model's encoding ability with the generation
budget it was given.

This effect is specific to reasoning ("thinking") configurations. Non-reasoning models emit
the function directly and finish well inside a small budget, so their numbers
are budget-insensitive.

## How truncation is detected

For each response we record `tokens_out`. A response is counted as **truncated**
when it (a) reached the budget (`tokens_out >= max_tokens - 500`) **and**
(b) yielded no extractable/parseable `build_oracle`. This separates budget
truncation from ordinary format/syntax failures (a response that stops well
under the cap but still has no usable code is a model error, not truncation).

## Measured truncation, frozen_v1.0 (480 instances)

| Configuration | `max_tokens` | truncated | share | L1 (parse) | note |
|---|---:|---:|---:|---:|---|
| Qwen2.5-Coder-7B (no-think) | 3000 | 0 | 0% | 100% | budget-insensitive |
| Qwen2.5-Coder-32B (no-think) | 3000 | 0 | 0% | 100% | budget-insensitive |
| Qwen3-32B (no-think) | 3000 | 0 | 0% | 99.8% | budget-insensitive |
| Qwen3-32B (thinking) | 28000 | 0 | 0% | 99.8% | fits; median CoT ≈ 17k |
| DeepSeek-R1-0528-Qwen3-8B | 32000 | ~1 | 0.2% | 99.8%¹ | not truncation-limited |
| gpt-oss-20b (high) | 32000 | 313 | 65% | 34.8% | severe; re-run at 90k |
| gpt-oss-20b (high) | 90000 | 40 | 8.3% | 90.0² | residual, counted as failures |
| gpt-oss-120b (high) | 32000 | 85 | 17.7% | 82.3% | partial; targeted re-run |

¹ R1's raw-extraction rate is 99.8%, but its **verifier** L1 is 86.0%: ~14% of
responses parse into a code block that then fails the syntax/API gate. That is a
model error, not truncation (only ~1 empty response).
² The 90k figures are the shipped final row (full 90k re-run plus targeted
retries): 8.3% of instances still hit the cap without emitting code and are
counted as failures.

The smaller reasoning model rambles far more than the larger one: gpt-oss-20b at
"high" effort truncates 65% of responses at 32k (median output pinned to the
cap), whereas gpt-oss-120b truncates 17.7% (median CoT ≈ 20k). The two
non-truncation cases (Qwen3-32B-thinking, R1) confirm that a sufficient budget
makes a configuration budget-insensitive.

## Impact on the reported number

Truncated responses fail L1, so they drag L3 down one-for-one. At the 32k
budget gpt-oss-120b's whole-set L3 was budget-limited; after the targeted
re-runs below its shipped row is L3 = 81.2 with a residual 2.1% of instances
still at the cap (counted as failures). gpt-oss-20b's shipped row is
L3 = 68.8 with a residual 8.3% at the cap.

## Mitigation

Two options, both used here:

1. **Raise the budget and re-run** (used for gpt-oss-20b: 32k → 90k). Correct
   but expensive; a full high-budget reasoning pass over 480 instances is slow.

2. **Targeted re-run of the truncated instances only** (used for gpt-oss-120b).
   Keep the untruncated responses; re-generate just the truncated task ids at a
   larger budget and splice them back in. For gpt-oss-120b that is 85 instances
   at 64k and a residual 39 at 90k instead of a full 480-instance pass — the
   same fair number at a fraction of the cost. The per-round components are
   under `runs_provenance/`.

### Serving constraint behind the choice

gpt-oss-120b cannot simply be moved to a larger GPU to make the high-budget run
cheap. On the H100 (80 GB) the MXFP4 weights (~63 GB) leave little room for the
KV cache, so a large `max_tokens` admits only a few concurrent sequences and the
pass is slow. On the B200 (180 GB) there is ample KV room, but the gpt-oss MXFP4
path there (FlashInfer TRTLLM) fails at CUDA-graph capture for these shapes
(`getValidConfigIndices: No valid config found`), whereas the H100 Marlin MXFP4
path is stable. The AWQ-Marlin path used for the 235B model does run on the
B200. Hence gpt-oss-120b's fair number is obtained by the targeted-re-run
approach on the H100 rather than a full high-budget pass.

## Recommended budgets

| Configuration | recommended `max_tokens` |
|---|---|
| non-reasoning (direct code) | 3000 |
| Qwen3-32B thinking | 28000 (fits) |
| DeepSeek-R1-0528-Qwen3-8B | 32000 (fits) |
| gpt-oss-20b / -120b (high effort) | ≥ 64000; verbose CoT needs headroom |

## Reporting convention

Report the budget alongside each reasoning configuration's pass rate, and flag
any configuration whose truncation share is non-negligible. A reasoning
configuration's semantic pass@1 is
only comparable across models once every configuration is run at a budget large enough
that its truncation share is ≈ 0.
