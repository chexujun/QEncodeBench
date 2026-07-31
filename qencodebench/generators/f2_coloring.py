"""F2: graph 3-coloring with the surjective 2-bit color code.

Color code per vertex v (2 qubits, little-endian):
    qubit 2v   = low bit b0,  qubit 2v+1 = high bit b1
    code value c = b0 + 2*b1;   decoded color = 0 if c in {0, 3} else c
    i.e. the surjective map 11 -> color 0.  All 2^(2V) codes are legal.

f(x) = 1 iff the DECODED colors form a proper coloring (all edges bichromatic).

Qubit account (family formulas, global cap 20):
    T1/T2 (per-edge flags):  2V + E + 1
    T3   (counter encoding): 2V + ceil(log2(E+1)) + 1   (shared edge flag)
The reference oracles use one qubit less than the budget in the T1/T2 case
(the +1 is kickback slack for models that prefer a final AND ancilla).
"""

from __future__ import annotations

import itertools
import random

from qiskit import QuantumCircuit

from qencodebench.core.task import (
    TaskInstance, TaskGenerator, GeneratorReject, stable_rng_seed,
    GLOBAL_QUBIT_CAP, tier_label,
)
from qencodebench.core.circuits import (
    flag_colors_differ, phase_on_pattern, controlled_increment,
    controlled_decrement, decode_color, counter_width,
)

MAX_TRIES = 800

# T1 includes V=5 (design range starts at 4 problem-qubit pairs; V=3/4
# alone offer < 35 distinct isolated-vertex-free graphs, fewer than the
# frozen-set tier quota once specs are deduplicated).
TIER_PARAMS = {
    1: dict(v_choices=[3, 4, 5], e_range=(3, 4)),
    2: dict(v_choices=[4, 5], e_range=(5, 9)),
    3: dict(v_choices=[5, 6], e_range=(7, 12)),
}


class ColoringGenerator(TaskGenerator):
    family = "coloring"
    tiers = (1, 2, 3)

    def generate(self, tier: int, seed: int) -> TaskInstance:
        params = TIER_PARAMS[tier]
        for sub in range(MAX_TRIES):
            rng = random.Random(stable_rng_seed(self.family, tier, seed, sub))
            v = rng.choice(params["v_choices"])
            lo, hi = params["e_range"]
            e = rng.randint(lo, min(hi, v * (v - 1) // 2))
            edges = sorted(rng.sample(list(itertools.combinations(range(v), 2)), e))
            if self._has_isolated_vertex(v, edges):
                self._record_reject(tier, seed, sub, "isolated_vertex")
                continue
            if tier >= 3:
                budget = 2 * v + counter_width(e) + 1
            else:
                budget = 2 * v + e + 1
            if budget > GLOBAL_QUBIT_CAP:
                self._record_reject(tier, seed, sub, f"budget:{budget}")
                continue
            spec = {"n_vertices": v, "edges": [list(t) for t in edges],
                    "encoding": "counter" if tier >= 3 else "edge_flags"}
            inst = TaskInstance(
                task_id=f"coloring-{tier_label(tier)}-s{seed:04d}",
                family=self.family, tier=tier, seed=seed,
                problem_text="", formal_spec=spec,
                n_problem_qubits=2 * v,
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
        raise RuntimeError(f"coloring T{tier} s{seed}: retries exhausted")

    @staticmethod
    def _has_isolated_vertex(v: int, edges) -> bool:
        touched = {u for edge in edges for u in edge}
        return len(touched) < v

    def classical_solutions(self, inst: TaskInstance) -> set[int]:
        v = inst.formal_spec["n_vertices"]
        edges = inst.formal_spec["edges"]
        sols = set()
        for x in range(1 << (2 * v)):
            colors = [decode_color((x >> (2 * i)) & 0b11) for i in range(v)]
            if all(colors[a] != colors[b] for a, b in edges):
                sols.add(x)
        return sols

    def reference_oracle(self, inst: TaskInstance) -> QuantumCircuit:
        v = inst.formal_spec["n_vertices"]
        edges = inst.formal_spec["edges"]
        e = len(edges)
        cell = lambda i: (2 * i, 2 * i + 1)          # noqa: E731

        if inst.formal_spec["encoding"] == "edge_flags":
            qc = QuantumCircuit(2 * v + e)
            flags = list(range(2 * v, 2 * v + e))

            def compute():
                for j, (a, b) in enumerate(edges):
                    flag_colors_differ(qc, cell(a), cell(b), flags[j])

            compute()
            phase_on_pattern(qc, flags, [1] * e)
            compute()                                 # involution
            return qc

        # counter encoding (T3): count satisfied edges, phase on count == E
        w = counter_width(e)
        qc = QuantumCircuit(2 * v + 1 + w)
        flag = 2 * v
        counter = list(range(2 * v + 1, 2 * v + 1 + w))

        for a, b in edges:
            flag_colors_differ(qc, cell(a), cell(b), flag)
            controlled_increment(qc, [flag], counter)
            flag_colors_differ(qc, cell(a), cell(b), flag)
        phase_on_pattern(qc, counter, [(e >> i) & 1 for i in range(w)])
        for a, b in reversed(edges):
            flag_colors_differ(qc, cell(a), cell(b), flag)
            controlled_decrement(qc, [flag], counter)
            flag_colors_differ(qc, cell(a), cell(b), flag)
        return qc


# ---- problem-text rendering -------------------------------------------------

_CODE_TABLE = (
    "Color code per vertex v (2 qubits): low bit b0 = problem_qubits[2v], "
    "high bit b1 = problem_qubits[2v+1]; code value c = b0 + 2*b1.\n"
    "Decoding is SURJECTIVE: c=0 (binary 00) -> color 0, c=1 (01) -> color 1, "
    "c=2 (10) -> color 2, and c=3 (binary 11) ALSO decodes to color 0.\n"
    "All 2-bit codes are legal; there is no invalid code.\n"
    "Worked example with the 11 code: if vertex 0 has code 11 and vertex 1 "
    "has code 00, both decode to color 0, so an edge (0,1) would be "
    "monochromatic and the constraint 'colors differ' is VIOLATED."
)


def render_verbose(spec: dict) -> str:
    v, edges = spec["n_vertices"], spec["edges"]
    lines = [
        f"We have an undirected graph with {v} vertices (numbered 0..{v-1}) "
        f"and {len(edges)} edges:",
        "  edges = " + ", ".join(f"({a},{b})" for a, b in edges),
        "",
        "Each vertex must receive one of 3 colors (0, 1, 2).",
        _CODE_TABLE,
        "",
        "The classical predicate is f(x) = 1 if and only if, after decoding "
        "every vertex's 2-bit code to its color, every edge connects two "
        "vertices of DIFFERENT colors.",
    ]
    return "\n".join(lines)


def render_terse(spec: dict) -> str:
    v, edges = spec["n_vertices"], spec["edges"]
    return (
        f"Graph 3-coloring, V={v}, edges={edges}. Vertex v encoded on 2 "
        f"qubits (b0=problem_qubits[2v], b1=problem_qubits[2v+1]), code "
        f"c=b0+2*b1, surjective decode: 00->0, 01->1, 10->2, 11->0 "
        f"(11 and 00 are the SAME color). f(x)=1 iff all edges get "
        f"different decoded colors. Example: codes 11 vs 00 on an edge "
        f"violate the constraint."
    )
