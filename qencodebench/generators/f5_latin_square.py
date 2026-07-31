"""F5: 3x3 Latin-square completion puzzle with the surjective cell code.

Puzzle form: part of the grid is GIVEN, only the
free cells (<= 6) are encoded.  Cell values are 0/1/2 with the surjective
2-bit code shared with F2: 00 -> 0, 01 -> 1, 10 -> 2, 11 -> 0.

Free cell number j (j-th entry of free_cells) uses problem qubits
(2j, 2j+1) = (low bit, high bit).

f(x) = 1 iff after decoding all free cells the full 3x3 grid is a Latin
square (each row and each column contains 0, 1, 2 exactly once).

Qubit account:
    T1/T2 (per-constraint flags): 2F + P + 1     (P = pairwise constraints)
    T3   (counter encoding):      2F + ceil(log2(P+1)) + 2
"""

from __future__ import annotations

import random

from qiskit import QuantumCircuit

from qencodebench.core.task import (
    TaskInstance, TaskGenerator, GeneratorReject, stable_rng_seed,
    GLOBAL_QUBIT_CAP, tier_label,
)
from qencodebench.core.circuits import (
    flag_colors_differ, flag_cell_differs_const, phase_on_pattern,
    controlled_increment, controlled_decrement, decode_color, counter_width,
)

MAX_TRIES = 2000

# Yield-rule adjustment: exhaustive feasibility scan over all
# 12 squares x C(9,F) free-cell choices shows (a) F=4 always has >= 12
# pairwise constraints, so the pair-flags budget 2F+P+1 exceeds 20, and
# (b) F >= 5 can never reach solution density >= 1/64 over the 2^(2F) code
# space.  Tiers are therefore F=2 / F=3 (pair flags) / F=4 (counter).
TIER_PARAMS = {
    1: dict(f_choices=[2], encoding="pair_flags"),
    2: dict(f_choices=[3], encoding="pair_flags"),
    3: dict(f_choices=[4], encoding="counter"),
}

_LINES = [[(r, 0), (r, 1), (r, 2)] for r in range(3)] + \
         [[(0, c), (1, c), (2, c)] for c in range(3)]


def _random_latin_square(rng: random.Random) -> list[list[int]]:
    row0 = rng.sample(range(3), 3)
    # second row: a permutation clashing nowhere with row0
    candidates = [p for p in
                  ([row0[1], row0[2], row0[0]], [row0[2], row0[0], row0[1]])]
    row1 = rng.choice(candidates)
    row2 = [3 - row0[c] - row1[c] for c in range(3)]
    return [row0, row1, row2]


def constraints_of(spec: dict) -> list[tuple]:
    """Pairwise all-different constraints touching at least one free cell.

    Returns tuples ("pair", j1, j2) or ("const", j, value)."""
    grid = spec["grid"]                      # 3x3, None for free cells
    free = [tuple(c) for c in spec["free_cells"]]
    index = {cell: j for j, cell in enumerate(free)}
    out = []
    for line in _LINES:
        for a in range(3):
            for b in range(a + 1, 3):
                ca, cb = line[a], line[b]
                fa, fb = ca in index, cb in index
                if fa and fb:
                    out.append(("pair", index[ca], index[cb]))
                elif fa:
                    out.append(("const", index[ca], grid[cb[0]][cb[1]]))
                elif fb:
                    out.append(("const", index[cb], grid[ca[0]][ca[1]]))
    return out


class LatinSquareGenerator(TaskGenerator):
    family = "latin_square"

    def generate(self, tier: int, seed: int) -> TaskInstance:
        params = TIER_PARAMS[tier]
        for sub in range(MAX_TRIES):
            rng = random.Random(stable_rng_seed(self.family, tier, seed, sub))
            square = _random_latin_square(rng)
            f = rng.choice(params["f_choices"])
            cells = [(r, c) for r in range(3) for c in range(3)]
            free = sorted(rng.sample(cells, f))
            grid = [[square[r][c] if (r, c) not in free else None
                     for c in range(3)] for r in range(3)]
            spec = {"grid": grid, "free_cells": [list(c) for c in free],
                    "encoding": params["encoding"]}
            p = len(constraints_of(spec))
            if params["encoding"] == "pair_flags":
                budget = 2 * f + p + 1
            else:
                budget = 2 * f + counter_width(p) + 2
            if budget > GLOBAL_QUBIT_CAP:
                self._record_reject(tier, seed, sub, f"budget:{budget}")
                continue
            inst = TaskInstance(
                task_id=f"latin_square-{tier_label(tier)}-s{seed:04d}",
                family=self.family, tier=tier, seed=seed,
                problem_text="", formal_spec=spec,
                n_problem_qubits=2 * f,
                max_total_qubits=budget,
                max_depth=0,
            )
            try:
                self._check_instance(inst, self.classical_solutions(inst))
            except GeneratorReject as ex:
                self._record_reject(tier, seed, sub, ex.reason)
                continue
            inst.problem_text = render_verbose(spec)
            return self.finalize(inst)
        raise RuntimeError(f"latin_square T{tier} s{seed}: retries exhausted")

    def classical_solutions(self, inst: TaskInstance) -> set[int]:
        spec = inst.formal_spec
        grid = spec["grid"]
        free = [tuple(c) for c in spec["free_cells"]]
        f = len(free)
        sols = set()
        for x in range(1 << (2 * f)):
            full = [row[:] for row in grid]
            for j, (r, c) in enumerate(free):
                full[r][c] = decode_color((x >> (2 * j)) & 0b11)
            ok = all(sorted(full[r]) == [0, 1, 2] for r in range(3)) and \
                all(sorted(full[r][c] for r in range(3)) == [0, 1, 2]
                    for c in range(3))
            if ok:
                sols.add(x)
        return sols

    def reference_oracle(self, inst: TaskInstance) -> QuantumCircuit:
        spec = inst.formal_spec
        f = len(spec["free_cells"])
        cons = constraints_of(spec)
        p = len(cons)
        cell = lambda j: (2 * j, 2 * j + 1)          # noqa: E731

        def apply_constraint(qc, con, target):
            if con[0] == "pair":
                flag_colors_differ(qc, cell(con[1]), cell(con[2]), target)
            else:
                flag_cell_differs_const(qc, cell(con[1]), con[2], target)

        if spec["encoding"] == "pair_flags":
            qc = QuantumCircuit(2 * f + p)
            flags = list(range(2 * f, 2 * f + p))

            def compute():
                for j, con in enumerate(cons):
                    apply_constraint(qc, con, flags[j])

            compute()
            phase_on_pattern(qc, flags, [1] * p)
            compute()                                # involution
            return qc

        w = counter_width(p)
        qc = QuantumCircuit(2 * f + 1 + w)
        flag = 2 * f
        counter = list(range(2 * f + 1, 2 * f + 1 + w))
        for con in cons:
            apply_constraint(qc, con, flag)
            controlled_increment(qc, [flag], counter)
            apply_constraint(qc, con, flag)
        phase_on_pattern(qc, counter, [(p >> i) & 1 for i in range(w)])
        for con in reversed(cons):
            apply_constraint(qc, con, flag)
            controlled_decrement(qc, [flag], counter)
            apply_constraint(qc, con, flag)
        return qc


# ---- problem-text rendering -------------------------------------------------

_CODE_TABLE = (
    "Cell value code (2 qubits per free cell): free cell number j uses low "
    "bit b0 = problem_qubits[2j] and high bit b1 = problem_qubits[2j+1]; "
    "code c = b0 + 2*b1.\n"
    "Decoding is SURJECTIVE: 00 -> value 0, 01 -> value 1, 10 -> value 2, "
    "and 11 ALSO decodes to value 0.  All codes are legal.\n"
    "Worked example with the 11 code: if a free cell has code 11 it holds "
    "value 0; placing it in a row that already contains a given 0 VIOLATES "
    "the all-different constraint."
)


def _grid_str(grid) -> str:
    return "\n".join(
        "  " + " ".join("." if v is None else str(v) for v in row)
        for row in grid
    )


def render_verbose(spec: dict) -> str:
    free = spec["free_cells"]
    return "\n".join([
        "We must complete a 3x3 Latin square: every row and every column "
        "must contain the values 0, 1, 2 exactly once.",
        "The partially filled grid is (rows top to bottom, '.' = free cell):",
        _grid_str(spec["grid"]),
        "",
        "The free cells, in order, are (row, col): "
        + ", ".join(f"({r},{c})" for r, c in free)
        + f".  Free cell number j is the j-th in this list.",
        _CODE_TABLE,
        "",
        "The classical predicate is f(x) = 1 if and only if decoding all "
        "free cells yields a completed grid that is a valid Latin square.",
    ])


def render_terse(spec: dict) -> str:
    return (
        f"3x3 Latin square completion. Grid (None=free): {spec['grid']}, "
        f"free_cells={spec['free_cells']} (cell j on qubits 2j,2j+1; code "
        f"c=b0+2*b1, surjective decode 00->0, 01->1, 10->2, 11->0). "
        f"f(x)=1 iff completed grid has each row and column containing "
        f"0,1,2 exactly once."
    )
