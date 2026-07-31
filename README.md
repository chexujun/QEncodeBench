# QEncodeBench

Code and data for the paper **"QEncodeBench: Can Large Language Models
Encode Classical Problems into Verified Quantum Oracles?"**
(Xujun Che, Hanhan Wu, Yuchen Yuan, Chenyang Yu).

QEncodeBench tasks LLMs with encoding classical constraint problems as
Grover-style phase oracles and scores the generated circuits with an
adversarially self-validated verifier that decides full solution-set
equivalence up to a global phase, with ancillas restored and resource
budgets enforced.

## Layout

- `qencodebench/` — the benchmark package: task/instance model,
  prompt templates, four-gate verifier (fast path + exhaustive
  confirmation), unit-agent and NSC method scaffolds, run pipeline.
- `scripts/` — entry points: `run_eval.py` (evaluation),
  `build_frozen_set.py` / `build_frozen_v11.py` / `build_pilot_v11.py`
  (generators → frozen sets),
  `exhaustive_confirm.py` / `exhaustive_confirm_nonpipeline.py` /
  `exhaustive_confirm_retry.py` (the acceptance-confirmation
  harness), `prepare_terra_subagent_verbose_run.py`,
  `audit_e2_terra_verbose.py`, `verify_terra_proxy_final.py`,
  `scoring_degradation.py`, `report_v11_acceptance.py`.
- `configs/` — model registry and every run configuration.
- `data/` — frozen instance sets with golden solution sets:
  `frozen_v1/` (480-instance core), `frozen_v1_1/` (full v1.1 set:
  core + escalation; the 180 new instances alone are its
  `instances_new.jsonl`),
  `pilot_v11/` (escalation evaluation subset),
  `fresh_20260703/` (fresh regeneration set for the contamination
  control). Core, fresh, and escalation draw from disjoint seed
  domains.
- `runs/` — raw logs behind every reported number: per-run
  `config_snapshot.yaml`, `raw_responses.jsonl` (with extracted
  code), `verify_results.jsonl`; `runs/qeb_opensource_table2/` and
  `runs/claude_full480/` hold the open-weight and Claude rows
  with their audit records; `runs/e1_terra_subagent_proxy_480/` and
  `runs/e2_terra_subagent_proxy_verbose_480/` hold both Terra
  runs (prompts, per-instance SHA-256 manifest, responses,
  both verification records, and our independent re-verification);
  `runs/exhaustive_confirmation/` holds the per-sample logs showing
  that every accepted sample was confirmed by exhaustive
  per-basis-state simulation.
- `analysis/` — the verifier self-check report and the
  degraded-scoring study outputs; both regenerable offline
  (`python -m qencodebench.selfcheck.run_selfcheck`,
  `python scripts/scoring_degradation.py`).

## Environment

```
pip install -e .            # uses pyproject.toml
# or exactly pinned:
pip install -r requirements.lock.txt
```

## Quick start

Verify one delivered response end to end (extraction → four gates,
exhaustive verdict of record):

```
python - <<'PY'
import json
from qencodebench.core.task import TaskInstance
from qencodebench.pipeline.extract import extract_code
from qencodebench.verifier import verify_sample
inst = TaskInstance.from_dict(json.loads(open('data/frozen_v1/instances.jsonl').readline()))
sols = set(json.loads(open('data/frozen_v1/solutions.jsonl').readline())['solutions'])
resp = open('runs/e2_terra_subagent_proxy_verbose_480/responses/000_%s.md' % inst.task_id).read()
print(verify_sample(extract_code(resp), inst, sols))
PY
```

## Recomputing the paper

- Table 2 funnels/families/tiers: aggregate the per-run verification
  records under `runs/` by task metadata from
  `data/frozen_v1/instances.jsonl`.
- Tables 3-5 and Figure 3: the 126-task ladder merges each method's
  54-task pilot run with its 72-task extension run (the `e6_*`
  directories; each run's `config_snapshot.yaml` records its method,
  model, and reasoning mode). Direct reasoning-off numbers come from
  `e1_b_deepseek` restricted to the same subset.
- Degraded-scoring study: `scripts/scoring_degradation.py`.
- Escalation statistics: task-level best-of-3 with Clopper-Pearson
  intervals and Fisher exact contrasts over the three
  `v11_pilot_*` runs.
- Acceptance confirmation: `scripts/exhaustive_confirm.py`
  (pipeline-layout runs), `scripts/exhaustive_confirm_nonpipeline.py`
  (the open-weight, Claude, and first-Terra rows); the recorded
  outcomes are under `runs/exhaustive_confirmation/`
  (one `<name>.confirm.jsonl` per run), plus
  `runs/e2_terra_subagent_proxy_verbose_480/audit_reverify.jsonl`
  for the GPT-5.6 Terra row.
  `e1_terra_subagent_proxy_480.confirm.jsonl` belongs to the
  earlier, superseded Terra run and is retained for the record.

## Verifier self-validation

The adversarial mutant suite and self-check entry points live in the
verifier package; the live spot-check and freeze-on-disagreement
logic is in `qencodebench/verifier/verify.py`.

## License

MIT (see `LICENSE`). The frozen instance sets, golden solution sets,
and run logs are released under the same terms for research use.

## Citation

```bibtex
@misc{qencodebench2026,
  title  = {QEncodeBench: Can Large Language Models Encode Classical
            Problems into Verified Quantum Oracles?},
  author = {Che, Xujun and Wu, Hanhan and Yuan, Yuchen and Yu, Chenyang},
  year   = {2026},
  url    = {https://github.com/chexujun/QEncodeBench}
}
```
