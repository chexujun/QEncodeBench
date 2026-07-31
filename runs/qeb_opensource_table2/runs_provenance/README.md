# Budget-round components behind the merged gpt-oss rows

The final rows `runs/gptoss20b_final` and `runs/gptoss120b_final` keep,
per instance, the highest-budget attempt. Components:

```
gptoss20b/        full 480-instance run at max_tokens 90k
gptoss20b_fix/    37 targeted retries at 90k
gptoss120b/       initial 480-instance run at 32k (494 rows incl. retries)
gptoss120b_fix/   the 85 truncated instances re-run at 64k
gptoss120b_fix2/  the residual 39 instances re-run at 90k
```

Each component holds `raw_responses.jsonl` / `verify_results.jsonl` in the
standard schema. Methodology: `../token_budget_truncation.md`.
