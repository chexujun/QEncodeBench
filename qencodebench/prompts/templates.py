"""Frozen prompt templates.

The verbose template puts the fully STATIC prefix (role, task rules,
interface contract, toy example) first and the instance-specific
content (problem statement, resource budget) last, so provider input
caches hit on ~2/3 of the prompt.

The toy example is a PARITY oracle -- deliberately different from all six
benchmark families -- demonstrating the compute -> phase -> uncompute
skeleton and ancilla restoration.
"""

from __future__ import annotations

import hashlib

from qencodebench.core.task import TaskInstance
from qencodebench.generators import (
    f1_sat, f2_coloring, f3_vertex_cover, f4_subset_sum,
    f5_latin_square, f6_string_match, f7_sat_card,
)

_RENDERERS = {
    "sat_card": (f7_sat_card.render_verbose, f7_sat_card.render_terse),
    "3sat": (f1_sat.render_verbose, f1_sat.render_terse),
    "coloring": (f2_coloring.render_verbose, f2_coloring.render_terse),
    "vertex_cover": (f3_vertex_cover.render_verbose,
                     f3_vertex_cover.render_terse),
    "subset_sum": (f4_subset_sum.render_verbose, f4_subset_sum.render_terse),
    "latin_square": (f5_latin_square.render_verbose,
                     f5_latin_square.render_terse),
    "string_match": (f6_string_match.render_verbose,
                     f6_string_match.render_terse),
}

TOY_EXAMPLE = '''\
## Worked toy example (a DIFFERENT problem: parity)

Suppose f(x) = x0 XOR x1 over 2 problem qubits (mark states 01 and 10).
A correct implementation computes the predicate into an ancilla, applies a
Z gate for the phase, then UNCOMPUTES the ancilla so it ends in |0>:

```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    a = ancilla_qubits[0]
    qc.cx(problem_qubits[0], a)   # compute: a = x0 xor x1
    qc.cx(problem_qubits[1], a)
    qc.z(a)                       # phase: -1 iff a == 1
    qc.cx(problem_qubits[1], a)   # uncompute (mirror of compute)
    qc.cx(problem_qubits[0], a)
```
'''

# ---- fully static blocks (cacheable prefix) ---------------------------------

_VERBOSE_STATIC = '''\
You are an expert quantum programmer.

## Your task

Implement a Grover-style PHASE ORACLE for the classical problem given at
the end of this prompt, as a Python function using Qiskit:

```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    ...
```

Semantics (must hold EXACTLY, for every computational basis state):
- For each basis state |x> with f(x) = 1, apply phase -1; leave every basis
  state with f(x) = 0 unchanged.  (An overall global phase on the whole
  oracle is irrelevant and accepted.)
- Bit i of x lives on problem_qubits[i] (x = sum_i x_i * 2^i).
- EVERY ancilla qubit must be returned to |0> for every input (use the
  compute -> phase -> uncompute discipline).
- The oracle must be a diagonal operator in the computational basis: no
  measurement, no reset, and it must not permute or mix basis states.

Rules:
- Build the circuit by appending standard gates to `qc` in place
  (x, cx, ccx, mcx, z, cz, h, p, mcp, ...).  Do not create a new circuit,
  do not add registers, do not measure.
- FORBIDDEN (checked and rejected): qc.unitary, qc.diagonal, qc.initialize,
  qc.prepare_state, UnitaryGate, qiskit.quantum_info (Operator/Statevector),
  and classical brute-force enumeration of all solutions baked into gates.
- Allowed imports: qiskit, numpy, math.

Output format: reply with ONE ```python code block containing the complete
build_oracle function (plus any imports it needs). No other code.

'''

_TERSE_STATIC = '''\
Implement in Qiskit:
def build_oracle(qc, problem_qubits, ancilla_qubits) -> None
Apply phase -1 to every basis state |x> with f(x)=1 (bit i of x on
problem_qubits[i]); leave f(x)=0 states unchanged; global phase irrelevant.
All ancillas must end in |0> for every input. Diagonal operator only: no
measure/reset/basis mixing. In-place standard gates only; qc.unitary /
qc.diagonal / qc.initialize / UnitaryGate / quantum_info are rejected.
Reply with one ```python code block containing build_oracle.

'''

_BUDGET_BLOCK = '''\

## Resource budget for this instance

- {budget} total qubits are provided: {n} problem qubits + {n_anc} ancillas.
- Transpiled depth (basis ['rz','sx','x','cx'], optimization_level=1) must
  be at most {max_depth}.
'''


def render_problem_text(inst: TaskInstance, variant: str = "verbose") -> str:
    verbose, terse = _RENDERERS[inst.family]
    return verbose(inst.formal_spec) if variant == "verbose" \
        else terse(inst.formal_spec)


def build_prompt(inst: TaskInstance, variant: str = "verbose") -> str:
    n = inst.n_problem_qubits
    fields = dict(budget=inst.max_total_qubits, n=n,
                  n_anc=inst.max_total_qubits - n, max_depth=inst.max_depth)
    problem = render_problem_text(inst, variant)
    budget_block = _BUDGET_BLOCK.format(**fields)
    if variant == "verbose":
        return (_VERBOSE_STATIC + TOY_EXAMPLE
                + "\n## Problem\n\n" + problem + "\n" + budget_block)
    return (_TERSE_STATIC + "## Problem\n" + problem + "\n" + budget_block)


def prompt_sha256(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()
