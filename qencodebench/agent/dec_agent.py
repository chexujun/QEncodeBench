"""DEC-Agent: Decompose-Encode-Check.

Stage 1  classicalise: LLM writes a classical checker f_py; it is compared
         against classical_solutions on ALL 2^n inputs (free, deterministic);
         on mismatch, counterexample feedback and retry (<= 2 retries).
Stage 2  synthesise: LLM translates the validated checker into build_oracle
         following the compute -> phase -> uncompute skeleton.
Stage 3  verify-repair: the semantic verifier produces (fail level,
         stratified counterexamples, mark accuracy); feedback loop
         (<= 3 rounds).  Feedback is FIXED-LENGTH: current code + failure
         summary + <= 8 counterexamples + one-line repair history entries
         (no full conversation replay).

The self-repair baseline is stage 3 alone applied to a direct generation
(isolates "feedback" from "decomposition").

Per-sample total-token cap: 25K; exceeding it records
AGENT_BUDGET_EXCEEDED.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys

from qencodebench.core.task import TaskInstance
from qencodebench.pipeline.extract import extract_code
from qencodebench.pipeline.llm import MockClient
from qencodebench.prompts import build_prompt
from qencodebench.verifier import verify_sample

MAX_STAGE1_RETRIES = 2
MAX_REPAIR_ROUNDS = 3
TOKEN_CAP = 25_000
MAX_FEEDBACK_CE = 8
AGENT_MAX_TOKENS = 2000     # per-call output cap in agent loops


# ---------------------------------------------------------------------------
# stage 1: classical checker
# ---------------------------------------------------------------------------

STAGE1_PROMPT = '''\
{problem}

## Stage 1: classical checker

Before any quantum code, write a PURE-PYTHON checker for the predicate above:

```python
def check(x: int) -> bool:
    ...
```

Bit i of x (i.e. (x >> i) & 1) is the value of problem qubit i exactly as
described in the problem statement.  Return True iff f(x) = 1.
No imports except math.  Reply with ONE ```python code block.
'''

STAGE1_FEEDBACK = '''\
Your checker disagrees with the problem specification on these inputs:
{cases}
Fix `check` and reply with ONE ```python code block containing the full
corrected function.
'''


def run_classical_check(code: str, n: int,
                        timeout_s: int = 20) -> set[int] | str:
    """Evaluate `check` on all 2^n inputs in a subprocess.
    Returns the accepted set, or an error string."""
    driver = (
        f"{code}\n\n"
        "import json\n"
        f"_res = [x for x in range({1 << n}) if check(x)]\n"
        "print('QEB_RESULT:' + json.dumps(_res))\n"
    )
    try:
        proc = subprocess.run([sys.executable, "-"], input=driver,
                              capture_output=True, text=True,
                              timeout=timeout_s)
    except subprocess.TimeoutExpired:
        return "checker timed out"
    for line in proc.stdout.splitlines():
        if line.startswith("QEB_RESULT:"):
            return set(json.loads(line[len("QEB_RESULT:"):]))
    return f"checker crashed: {proc.stderr[-500:]}"


def _extract_check(text: str) -> str | None:
    """Extract the last fenced block containing `def check`."""
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, re.DOTALL)
    for b in reversed(blocks):
        if "def check" in b:
            return b.strip()
    return text.strip() if "def check" in text else None


def _fmt_cases(mism: list[tuple[int, bool]], n: int) -> str:
    lines = []
    for x, expected in mism[:MAX_FEEDBACK_CE]:
        bits = ", ".join(f"q{i}={(x >> i) & 1}" for i in range(n))
        lines.append(f"- x={x} ({bits}): expected f(x)={int(expected)}, "
                     f"your checker returned {int(not expected)}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# stage 2 / 3 prompts
# ---------------------------------------------------------------------------

STAGE2_SUFFIX = '''\

## Stage 2: constraint-by-constraint synthesis

The following classical checker has been VALIDATED against the full
specification -- treat it as the ground-truth definition of f:

```python
{checker}
```

Translate it into the phase oracle: implement each constraint as a
reversible fragment (compute a flag ancilla), combine the flags for the
phase (compute -> phase -> uncompute), and mirror-uncompute every ancilla.
'''

REPAIR_PROMPT = '''\
Your oracle implementation FAILED verification.

## Current code
```python
{code}
```

## Verifier feedback
- failure level: {level}  (reason: {reason})
- fraction of basis states with correct phase behaviour: {acc}
{diff}
{cases}

## Previous repair attempts
{history}

Rules reminder: phase -1 exactly on f(x)=1 basis states (global phase
irrelevant); all ancillas back to |0>; in-place standard gates only; at most
{budget} total qubits; transpiled depth <= {max_depth}.

Reply with ONE ```python code block containing the FULL corrected
build_oracle, then a final line:
SUMMARY: <at most 20 words describing what you changed>
'''


def _fmt_verifier_cases(row: dict, inst: TaskInstance,
                        solutions: set[int]) -> str:
    ces = row.get("counterexamples") or []
    if not ces:
        return ""
    n = inst.n_problem_qubits
    lines = ["- wrongly handled basis states:"]
    for x in ces[:MAX_FEEDBACK_CE]:
        should = x in solutions
        kind = ("should be marked but is not" if should
                else "must NOT be marked but is")
        bits = ", ".join(f"q{i}={(x >> i) & 1}" for i in range(n))
        lines.append(f"  - x={x} ({bits}): {kind}")
    return "\n".join(lines)


def _summary_line(text: str) -> str:
    for line in reversed(text.strip().splitlines()):
        if line.strip().upper().startswith("SUMMARY:"):
            return line.strip()[len("SUMMARY:"):].strip()[:160]
    return "(no summary provided)"


# ---------------------------------------------------------------------------
# agent driver
# ---------------------------------------------------------------------------

class TokenMeter:
    def __init__(self, cap: int = TOKEN_CAP):
        self.cap = cap
        self.total = 0

    def add(self, reply) -> None:
        self.total += reply.tokens_in + reply.tokens_out

    @property
    def exceeded(self) -> bool:
        return self.total > self.cap


def run_agent_sample(client, inst: TaskInstance, solutions: set[int],
                     method: str = "dec_agent",
                     temperature: float = 0.7,
                     prompt_variant: str = "verbose",
                     options: dict | None = None) -> dict:
    """Run one agent sample; returns a raw_responses-style row with
    agent_trace filled in.  ``method`` is 'dec_agent' or 'selfrepair'.

    ``options`` holds the ablation switches:
      skip_stage1_check (bool)  -- generate f_py but do not validate it
      max_repair_rounds (int)   -- 0 / 1 / 3
      feedback_counterexamples (bool) -- False = only "FAILED" is fed back
      repair_history (bool)     -- False = drop the attempted-repairs summary
    """
    assert method in ("dec_agent", "selfrepair")
    opt = {"skip_stage1_check": False,
           "max_repair_rounds": MAX_REPAIR_ROUNDS,
           "feedback_counterexamples": True,
           "repair_history": True,
           # thinking-model combos need far more room than the default
           # 25K fuse (median thinking is ~11K tokens per call)
           "token_cap": TOKEN_CAP, **(options or {})}
    meter = TokenMeter(cap=opt["token_cap"])
    trace: list[dict] = []
    tokens = dict(tokens_in=0, tokens_out=0, cost_usd=0.0)

    def call(prompt: str):
        reply = client.complete(prompt, temperature,
                                max_tokens=AGENT_MAX_TOKENS)
        meter.add(reply)
        tokens["tokens_in"] += reply.tokens_in
        tokens["tokens_out"] += reply.tokens_out
        tokens["cost_usd"] += reply.cost_usd
        return reply

    checker: str | None = None
    problem = build_prompt(inst, prompt_variant)

    # ---- stage 1 (dec_agent only) -----------------------------------------
    if method == "dec_agent":
        if isinstance(client, MockClient):
            client.solutions = solutions
            client.n_problem = inst.n_problem_qubits
        prompt = STAGE1_PROMPT.format(problem=inst.problem_text)
        for attempt in range(MAX_STAGE1_RETRIES + 1):
            if meter.exceeded:
                break
            reply = call(prompt)
            checker = _extract_check(reply.text)
            if checker is None:
                trace.append({"stage": 1, "attempt": attempt,
                              "result": "no_checker_extracted"})
                continue
            if opt["skip_stage1_check"]:        # ablation: no validation loop
                trace.append({"stage": 1, "attempt": attempt,
                              "result": "unchecked (ablation)"})
                break
            got = run_classical_check(checker, inst.n_problem_qubits)
            if isinstance(got, str):
                trace.append({"stage": 1, "attempt": attempt,
                              "result": f"error: {got}"})
                prompt = (STAGE1_PROMPT.format(problem=inst.problem_text)
                          + f"\nYour previous checker failed: {got}\n")
                continue
            if got == solutions:
                trace.append({"stage": 1, "attempt": attempt,
                              "result": "validated"})
                break
            mism = ([(x, True) for x in sorted(solutions - got)]
                    + [(x, False) for x in sorted(got - solutions)])
            half = MAX_FEEDBACK_CE // 2
            mism = mism[:half] + mism[-half:] if len(mism) > MAX_FEEDBACK_CE \
                else mism
            trace.append({"stage": 1, "attempt": attempt,
                          "result": f"mismatch on {len(mism)}+ inputs"})
            prompt = (STAGE1_PROMPT.format(problem=inst.problem_text) + "\n"
                      + STAGE1_FEEDBACK.format(
                          cases=_fmt_cases(mism, inst.n_problem_qubits)))
        else:
            trace.append({"stage": 1, "result": "unvalidated_after_retries"})

    # ---- stage 2 / direct generation --------------------------------------
    if method == "dec_agent" and checker is not None:
        gen_prompt = problem + STAGE2_SUFFIX.format(checker=checker)
    else:
        gen_prompt = problem
    final_text, code = "", None
    if not meter.exceeded:
        reply = call(gen_prompt)
        final_text = reply.text
        code = extract_code(reply.text)
        trace.append({"stage": 2, "attempt": 0,
                      "result": "code_extracted" if code else "no_code"})

    # ---- stage 3: verify-repair loop ---------------------------------------
    history: list[str] = []
    max_rounds = opt["max_repair_rounds"]
    for rnd in range(max_rounds + 1):
        if meter.exceeded:
            break
        row = verify_sample(code, inst, solutions, model="agent",
                            method=method, sample_idx=rnd)
        passed = bool(row["pass"]["L3"]) and row["pass"]["L4"] is not False
        trace.append({"stage": 3, "attempt": rnd,
                      "level": row["level_reached"],
                      "fail_reason": row["fail_reason"],
                      "mark_accuracy": row["mark_accuracy"],
                      "result": "PASS" if passed else "FAIL"})
        if passed or rnd == max_rounds:
            break
        acc = row["mark_accuracy"]
        prompt = REPAIR_PROMPT.format(
            code=code or "(no code was extracted)",
            level=row["level_reached"],
            reason=row["fail_reason"],
            acc="n/a" if acc is None else f"{acc:.4f}",
            diff=(row.get("behavior_diff") or ""),
            cases=(_fmt_verifier_cases(row, inst, solutions)
                   if opt["feedback_counterexamples"] else ""),
            history=("\n".join(history) if history and
                     opt["repair_history"] else "(none)"),
            budget=inst.max_total_qubits,
            max_depth=inst.max_depth,
        )
        reply = call(prompt)
        final_text = reply.text
        new_code = extract_code(reply.text)
        summary = _summary_line(reply.text)
        verdict = "?" if new_code is None else "retry"
        history.append(f"R{rnd + 1}: {summary} -> was "
                       f"{row['fail_reason']}, acc {acc} [{verdict}]")
        if new_code is not None:
            code = new_code

    if meter.exceeded:
        trace.append({"stage": 3, "result": "AGENT_BUDGET_EXCEEDED",
                      "tokens": meter.total})

    return {
        "response_text": final_text,
        "extracted_code": code,
        "agent_trace": trace,
        "agent_budget_exceeded": meter.exceeded,
        **tokens,
    }
