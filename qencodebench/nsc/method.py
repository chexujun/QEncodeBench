"""NSC method driver: LLM emits IR -> classical validation (complete,
cheap) -> deterministic compile -> standard L1-L4 verification.

The LLM never writes gates.  Division of labour: the model does
NL -> formal spec (measured ~95% reliable in stage-1 data); the certified
compiler does formal -> reversible circuit.  This is the ceiling method of
the capability ladder.
"""

from __future__ import annotations

import json
import re

from qencodebench.core.task import TaskInstance
from qencodebench.nsc.ir import IR_DOC, IRError, evaluate, validate_schema
from qencodebench.nsc.compiler import emit_build_oracle_code, build_into  # noqa: F401

MAX_IR_RETRIES = 2

NSC_PROMPT = '''\
You are translating a constraint problem into a small Boolean IR (JSON).
You do NOT write any quantum code -- a certified compiler turns your IR
into the circuit.  Your only job: express the predicate f(x) EXACTLY.

## IR schema

{schema}

Conventions: variable bit i of x is qubit i.  For problems using 2-bit
cells (graph coloring / grid values), cell c occupies qubits 2c (low bit)
and 2c+1 (high bit) with the SURJECTIVE decode 00->0, 01->1, 10->2,
11->0; use the `cells_differ` / `cell_ne_const` atoms for those -- they
implement the surjective semantics for you.
IMPORTANT cell indexing: cell c means the c-th ENCODED cell exactly as
the problem statement numbers them (graph vertex v -> cell v; the j-th
FREE cell in the problem's free-cell list -> cell j).  It is NEVER a grid
coordinate; cells the problem lists as given/fixed are not encoded at
all and must be treated as constants via `cell_ne_const`.

## Worked example 1 (a different problem)

"f(x)=1 iff bit0 OR (NOT bit1), and additionally x has at most one 1-bit
among bits 0..2":

```json
{{"op": "and", "args": [
  {{"op": "or", "args": [{{"op": "bit", "i": 0, "val": 1}},
                          {{"op": "bit", "i": 1, "val": 0}}]}},
  {{"op": "linsum_cmp", "terms": [[1,0],[1,1],[1,2]], "cmp": "<=",
    "rhs": 1}}
]}}
```

## Worked example 2 (a different problem, with 2-bit cells)

"Three slots in a row; slots A and B are FREE (encoded as cell 0 and
cell 1, in the order the problem lists them), slot C is GIVEN with value
2; all three must be pairwise different":

```json
{{"op": "and", "args": [
  {{"op": "cells_differ", "a": 0, "b": 1}},
  {{"op": "cell_ne_const", "a": 0, "val": 2}},
  {{"op": "cell_ne_const", "a": 1, "val": 2}}
]}}
```
Note how the GIVEN slot never becomes a cell -- only free/encoded slots
get cell indices (0, 1, ... in listing order), and constraints against
given values use `cell_ne_const`.

## Problem

{problem}

Reply with ONE ```json code block containing only the IR object.
'''

IR_FEEDBACK = '''
Your previous IR was WRONG on these inputs:
{cases}
Reply with ONE ```json code block containing the corrected IR.
'''


def extract_ir(text: str) -> dict | None:
    blocks = re.findall(r"```(?:json)?\s*\n(.*?)```", text, re.DOTALL)
    for b in reversed(blocks):
        try:
            obj = json.loads(b)
            if isinstance(obj, dict) and "op" in obj:
                return obj
        except json.JSONDecodeError:
            continue
    try:
        obj = json.loads(text.strip())
        return obj if isinstance(obj, dict) and "op" in obj else None
    except json.JSONDecodeError:
        return None


def _mismatches(ir: dict, n: int, solutions: set[int],
                limit: int = 8) -> list[str]:
    out = []
    for x in range(1 << n):
        want = x in solutions
        if evaluate(ir, x) != want:
            bits = ", ".join(f"q{i}={(x >> i) & 1}" for i in range(n))
            out.append(f"- x={x} ({bits}): f must be {int(want)}, your IR "
                       f"gives {int(not want)}")
            if len(out) >= limit:
                break
    return out


def run_nsc_sample(client, inst: TaskInstance, solutions: set[int],
                   temperature: float = 0.7,
                   options: dict | None = None) -> dict:
    """One NSC sample; returns raw_responses-style fields.
    options: skip_validation -- compile the first schema-valid IR
    without the classical mismatch loop."""
    opt = {"skip_validation": False, **(options or {})}
    trace, tokens = [], dict(tokens_in=0, tokens_out=0, cost_usd=0.0)
    prompt = NSC_PROMPT.format(schema=IR_DOC, problem=inst.problem_text)
    text, code, ir = "", None, None
    last_valid_ir = None
    for attempt in range(MAX_IR_RETRIES + 1):
        reply = client.complete(prompt, temperature)
        text = reply.text
        for k in tokens:
            tokens[k] += getattr(reply, k)
        ir = extract_ir(reply.text)
        if ir is None:
            trace.append({"stage": "ir", "attempt": attempt,
                          "result": "no_ir_extracted"})
            prompt = (NSC_PROMPT.format(schema=IR_DOC,
                                        problem=inst.problem_text)
                      + "\nYour previous reply contained no valid JSON IR.")
            continue
        try:
            validate_schema(ir, inst.n_problem_qubits)
        except (IRError, KeyError, TypeError, ValueError) as e:
            trace.append({"stage": "ir", "attempt": attempt,
                          "result": f"schema_error: {e}"})
            prompt = (NSC_PROMPT.format(schema=IR_DOC,
                                        problem=inst.problem_text)
                      + f"\nYour previous IR was invalid: {e}\n")
            ir = None                       # never carry an invalid IR
            continue
        last_valid_ir = ir
        if opt["skip_validation"]:          # ablation: no classical check
            trace.append({"stage": "ir", "attempt": attempt,
                          "result": "unchecked (ablation)"})
            code = emit_build_oracle_code(ir)
            break
        try:
            mism = _mismatches(ir, inst.n_problem_qubits, solutions)
        except Exception as e:              # evaluate crash = schema gap
            trace.append({"stage": "ir", "attempt": attempt,
                          "result": f"evaluate_error: {e}"})
            prompt = (NSC_PROMPT.format(schema=IR_DOC,
                                        problem=inst.problem_text)
                      + f"\nYour previous IR could not be evaluated: {e}\n")
            continue
        if not mism:
            trace.append({"stage": "ir", "attempt": attempt,
                          "result": "validated"})
            code = emit_build_oracle_code(ir)
            break
        trace.append({"stage": "ir", "attempt": attempt,
                      "result": f"mismatch x{len(mism)}"})
        prompt = (NSC_PROMPT.format(schema=IR_DOC,
                                    problem=inst.problem_text)
                  + IR_FEEDBACK.format(cases="\n".join(mism)))
    else:
        if last_valid_ir is not None:   # best schema-VALID effort compiles
            code = emit_build_oracle_code(last_valid_ir)
            trace.append({"stage": "ir", "result": "unvalidated_final"})

    return {
        "response_text": text,
        "extracted_code": code,
        "agent_trace": trace,
        "agent_budget_exceeded": False,
        **tokens,
    }
