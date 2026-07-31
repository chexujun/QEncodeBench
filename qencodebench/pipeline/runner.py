"""Evaluation runner: generation + verification passes with
resumability, progress lines, budget fuses and completeness checks."""

from __future__ import annotations

import datetime as _dt
import json
import logging
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

import yaml

from qencodebench.core.task import TaskInstance
from qencodebench.pipeline.extract import extract_code
from qencodebench.pipeline.io import (
    append_jsonl, read_jsonl, load_instances, load_solutions,
)
from qencodebench.pipeline.llm import (
    make_client, MockClient, BudgetTracker, BudgetExceeded,
)
from qencodebench.prompts import build_prompt, prompt_sha256
from qencodebench.verifier import verify_sample

log = logging.getLogger("qencodebench.runner")

FEWSHOT_EXAMPLES = '''\
## Example A (parity of three bits)
f(x) = x0 xor x1 xor x2:
```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    a = ancilla_qubits[0]
    for q in problem_qubits[:3]:
        qc.cx(q, a)          # compute parity
    qc.z(a)                  # phase
    for q in reversed(problem_qubits[:3]):
        qc.cx(q, a)          # uncompute
```

## Example B (3-bit register value >= 5)
f(x) = 1 iff x in {5, 6, 7} = (x2 and x0) or (x2 and x1):
```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2 = problem_qubits[:3]
    a = ancilla_qubits[0]
    # a = x2 AND (x0 OR x1): compute OR via De Morgan into a, then AND
    qc.x(q0); qc.x(q1)
    qc.ccx(q0, q1, a)        # a = (not x0) and (not x1)
    qc.x(a)                  # a = x0 or x1
    qc.x(q0); qc.x(q1)
    qc.cz(q2, a)             # phase -1 iff x2 and a
    # uncompute a (mirror)
    qc.x(q0); qc.x(q1)
    qc.x(a)
    qc.ccx(q0, q1, a)
    qc.x(q0); qc.x(q1)
```
'''


@dataclass
class RunConfig:
    run_id: str
    instances_path: str
    solutions_path: str
    models: list[str]                      # keys into models.yaml
    method: str = "direct"                 # direct | fewshot | selfrepair | dec_agent
    prompt_variant: str = "verbose"
    n_samples: int = 1
    temperature: float = 0.0
    max_tokens: int = 4096
    run_budget_usd: float | None = None
    runs_dir: str = "runs"
    task_filter: list[str] = field(default_factory=list)
    task_sample: int | None = None    # stratified head: ~N/(family x tier)
    agent_options: dict = field(default_factory=dict)  # ablation switches
    concurrency: int = 1              # parallel API calls (direct/fewshot only)

    @classmethod
    def from_yaml(cls, path: str) -> "RunConfig":
        with open(path) as fh:
            raw = yaml.safe_load(fh)
        return cls(**raw)


def _load_models_cfg(path: str = "configs/models.yaml") -> dict:
    with open(path) as fh:
        return yaml.safe_load(fh)["models"]


def _sample_key(row: dict) -> tuple:
    return (row["task_id"], row["model"], row["method"],
            row["sample_idx"], row.get("prompt_variant", "verbose"))


def run_generation(cfg: RunConfig,
                   models_cfg: dict | None = None) -> str:
    """Query models for every (task, sample); resumable, budget-fused.
    Returns the run directory."""
    models_cfg = models_cfg or _load_models_cfg()
    run_dir = os.path.join(cfg.runs_dir, cfg.run_id)
    os.makedirs(run_dir, exist_ok=True)
    _setup_logging(run_dir)

    with open(os.path.join(run_dir, "config_snapshot.yaml"), "w") as fh:
        yaml.safe_dump(vars(cfg), fh)

    raw_path = os.path.join(run_dir, "raw_responses.jsonl")
    usage_path = os.path.join(run_dir, "api_usage.jsonl")
    # API-level errors are retried on resume; the agent budget
    # trip is terminal and counted as a failure instead.
    done = {_sample_key(r) for r in read_jsonl(raw_path)
            if not r.get("error") or r["error"] == "AGENT_BUDGET_EXCEEDED"}
    budget = BudgetTracker(usage_path, cfg.run_budget_usd)

    instances = load_instances(cfg.instances_path)
    solutions = load_solutions(cfg.solutions_path)
    if cfg.task_filter:
        instances = [i for i in instances if i.task_id in set(cfg.task_filter)]
    if cfg.task_sample:
        by_group: dict[tuple, list[TaskInstance]] = {}
        for inst in instances:
            by_group.setdefault((inst.family, inst.tier), []).append(inst)
        per_group = max(1, round(cfg.task_sample / len(by_group)))
        instances = [i for grp in by_group.values() for i in grp[:per_group]]

    total = len(instances) * len(cfg.models) * cfg.n_samples
    n_done, t0, spent0 = 0, time.time(), budget.global_total
    log.info("run %s: %d instances x %d models x %d samples = %d "
             "(already done: %d)", cfg.run_id, len(instances),
             len(cfg.models), cfg.n_samples, total, len(done))

    def one_sample(model_name: str, client, inst: TaskInstance,
                   sample_idx: int) -> tuple[dict, str] | None:
        if stop.is_set():          # budget fuse tripped: no NEW api calls
            return None
        t_start = time.time()
        if cfg.method in ("dec_agent", "selfrepair", "nsc", "unit_agent"):
            if cfg.method == "nsc":
                from qencodebench.nsc.method import run_nsc_sample
                agent_row = run_nsc_sample(
                    client, inst, solutions[inst.task_id],
                    temperature=cfg.temperature,
                    options=cfg.agent_options)
            elif cfg.method == "unit_agent":
                from qencodebench.agent.unit_agent import \
                    run_unit_agent_sample
                agent_row = run_unit_agent_sample(
                    client, inst, solutions[inst.task_id],
                    temperature=cfg.temperature,
                    options=cfg.agent_options)
            else:
                from qencodebench.agent.dec_agent import run_agent_sample
                agent_row = run_agent_sample(
                    client, inst, solutions[inst.task_id],
                    method=cfg.method,
                    temperature=cfg.temperature,
                    prompt_variant=cfg.prompt_variant,
                    options=cfg.agent_options)
            prompt = build_prompt(inst, cfg.prompt_variant)
            reply_fields = dict(
                response_text=agent_row["response_text"],
                extracted_code=agent_row["extracted_code"],
                agent_trace=agent_row["agent_trace"],
                tokens_in=agent_row["tokens_in"],
                tokens_out=agent_row["tokens_out"],
                cost_usd=agent_row["cost_usd"],
                latency_s=round(time.time() - t_start, 2),
                error=("AGENT_BUDGET_EXCEEDED"
                       if agent_row["agent_budget_exceeded"] else None),
            )
        else:
            prompt = build_prompt(inst, cfg.prompt_variant)
            if cfg.method == "fewshot":
                prompt = prompt + "\n" + FEWSHOT_EXAMPLES
            reply = client.complete(prompt, cfg.temperature, cfg.max_tokens)
            reply_fields = dict(
                response_text=reply.text,
                extracted_code=extract_code(reply.text),
                agent_trace=None,
                tokens_in=reply.tokens_in,
                tokens_out=reply.tokens_out,
                cost_usd=reply.cost_usd,
                latency_s=reply.latency_s,
                error=reply.error,
            )
        row = {
            "run_id": cfg.run_id,
            "task_id": inst.task_id,
            "model": model_name,
            "method": cfg.method,
            "sample_idx": sample_idx,
            "prompt_variant": cfg.prompt_variant,
            "prompt_sha256": prompt_sha256(prompt),
            "temperature": cfg.temperature,
            "timestamp": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            **reply_fields,
        }
        return row, model_name

    # Build the pending worklist (resume-aware).
    jobs: list[tuple] = []
    clients: dict[str, object] = {}
    for model_name in cfg.models:
        clients[model_name] = make_client(models_cfg[model_name])
        for inst in instances:
            for sample_idx in range(cfg.n_samples):
                key = (inst.task_id, model_name, cfg.method, sample_idx,
                       cfg.prompt_variant)
                if key in done:
                    n_done += 1
                else:
                    jobs.append((model_name, inst, sample_idx))

    # MockClient carries per-task state and stays sequential.  Agent
    # methods may run concurrently too (their wall time is dominated by
    # API latency; the local verifier interleaves) -- keep workers modest
    # for agent runs since each round also spends CPU on verification.
    workers = cfg.concurrency
    if any(isinstance(c, MockClient) for c in clients.values()):
        workers = 1

    write_lock = threading.Lock()
    stop = threading.Event()

    if budget.run_cap is not None and budget.run_total == 0 and \
            budget.global_total > 0:
        log.warning("resume note: this run dir has already spent $%.2f; "
                    "the per-run fuse ($%.2f) re-arms on resume by design "
                    "(pause-for-review semantics)", budget.global_total,
                    budget.run_cap)

    def record(row: dict, model_name: str) -> None:
        nonlocal n_done
        with write_lock:
            append_jsonl(raw_path, row)
            try:
                budget.record({
                    "run_id": cfg.run_id, "task_id": row["task_id"],
                    "model": model_name,
                    "tokens_in": row["tokens_in"],
                    "tokens_out": row["tokens_out"],
                    "cost_usd": row["cost_usd"],
                    "timestamp": row["timestamp"],
                })
            except BudgetExceeded as e:
                stop.set()
                log.error("BUDGET FUSE TRIPPED: %s -- run paused, resume "
                          "after review", e)
            n_done += 1
            if n_done % 20 == 0:
                _progress(n_done, total, t0, budget.global_total - spent0)

    if workers <= 1:
        for model_name, inst, sample_idx in jobs:
            if stop.is_set():
                break
            client = clients[model_name]
            if isinstance(client, MockClient):
                client.solutions = solutions[inst.task_id]
                client.n_problem = inst.n_problem_qubits
            row, mn = one_sample(model_name, client, inst, sample_idx)
            record(row, mn)
    else:
        log.info("generation with %d workers", workers)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = []
            for model_name, inst, sample_idx in jobs:
                if stop.is_set():
                    break
                futures.append(pool.submit(
                    one_sample, model_name, clients[model_name], inst,
                    sample_idx))
            for fut in as_completed(futures):
                try:
                    result = fut.result()
                except Exception as e:      # worker crash: log, keep going
                    log.error("worker failed: %s", e)
                    continue
                if result is None:          # skipped post-trip, no API call
                    continue
                # ALWAYS record completed work: its cost is already paid;
                # the fuse only stops NEW requests (workers check `stop`)
                record(*result)

    _completeness_check(run_dir, instances, cfg)
    return run_dir


def run_verification(run_dir: str, instances_path: str,
                     solutions_path: str) -> str:
    """Verify every raw response without an existing verify row."""
    _setup_logging(run_dir)
    raw_rows = read_jsonl(os.path.join(run_dir, "raw_responses.jsonl"))
    verify_path = os.path.join(run_dir, "verify_results.jsonl")
    done = {_sample_key(r) for r in read_jsonl(verify_path)}
    instances = {i.task_id: i for i in load_instances(instances_path)}
    solutions = load_solutions(solutions_path)

    todo, _seen = [], set(done)
    for r in raw_rows:
        key = _sample_key(r)
        if key in _seen or (r.get("error")
                            and r["error"] != "AGENT_BUDGET_EXCEEDED"):
            continue
        _seen.add(key)              # dedupe within this pass too
        todo.append(r)
    log.info("verification: %d rows to verify (%d already done)",
             len(todo), len(done))
    t0 = time.time()
    for i, raw in enumerate(todo, 1):
        inst = instances[raw["task_id"]]
        if raw.get("error") == "AGENT_BUDGET_EXCEEDED":
            # counted as a failure and reported separately
            row = verify_sample(None, inst, solutions[raw["task_id"]],
                                model=raw["model"], method=raw["method"],
                                sample_idx=raw["sample_idx"])
            row["fail_reason"] = "AGENT_BUDGET_EXCEEDED"
        else:
            row = verify_sample(
                raw.get("extracted_code"), inst, solutions[raw["task_id"]],
                model=raw["model"], method=raw["method"],
                sample_idx=raw["sample_idx"],
            )
        row["prompt_variant"] = raw.get("prompt_variant", "verbose")
        append_jsonl(verify_path, row)
        if i % 20 == 0:
            rates = _level_rates(read_jsonl(verify_path))
            log.info("verified %d/%d | pass rates %s | %.1fs elapsed",
                     i, len(todo), rates, time.time() - t0)
    log.info("verification complete: %d rows", len(todo))
    return verify_path


def _level_rates(rows: list[dict]) -> str:
    out = []
    for lvl in ("L1", "L2", "L3", "L4"):
        vals = [r["pass"][lvl] for r in rows if r["pass"][lvl] is not None]
        if vals:
            out.append(f"{lvl}:{sum(vals) / len(vals):.0%}")
    return " ".join(out)


def _progress(n_done: int, total: int, t0: float, spent: float) -> None:
    rate = n_done / max(time.time() - t0, 1e-9)
    eta_s = (total - n_done) / max(rate, 1e-9)
    log.info("progress %d/%d | spent $%.2f | ETA %s",
             n_done, total, spent,
             str(_dt.timedelta(seconds=int(eta_s))))


def _completeness_check(run_dir: str, instances: list[TaskInstance],
                        cfg: RunConfig) -> None:
    raw = read_jsonl(os.path.join(run_dir, "raw_responses.jsonl"))
    have = {_sample_key(r) for r in raw
            if not r.get("error") or r["error"] == "AGENT_BUDGET_EXCEEDED"}
    missing = []
    for model in cfg.models:
        for inst in instances:
            for s in range(cfg.n_samples):
                key = (inst.task_id, model, cfg.method, s, cfg.prompt_variant)
                if key not in have:
                    missing.append("\t".join(map(str, key)))
    log.info("completeness: expected %d, present %d, missing %d",
             len(instances) * len(cfg.models) * cfg.n_samples,
             len(have), len(missing))
    if missing:
        with open(os.path.join(run_dir, "missing.txt"), "w") as fh:
            fh.write("\n".join(missing) + "\n")


def _setup_logging(run_dir: str) -> None:
    root = logging.getLogger("qencodebench")
    if not any(isinstance(h, logging.FileHandler)
               and getattr(h, "_qeb_run", None) == run_dir
               for h in root.handlers):
        fh = logging.FileHandler(os.path.join(run_dir, "run.log"))
        fh._qeb_run = run_dir
        fh.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(message)s"))
        root.addHandler(fh)
    if not any(isinstance(h, logging.StreamHandler)
               and not isinstance(h, logging.FileHandler)
               for h in root.handlers):
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        root.addHandler(sh)
    root.setLevel(logging.INFO)
