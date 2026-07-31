"""F3: vertex cover of size <= k.

Encoding domain == problem domain: qubit i = vertex i in the cover (1) or not.
f(x) = 1 iff every edge has at least one endpoint in the cover AND
popcount(x) <= k.

Qubit account: n vertices + E edge flags + Hamming-weight counter
ceil(log2(n+1)).  Budget formula: n + E + counter_width(n), cap 20.
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
    flag_on_pattern, phase_on_pattern, controlled_increment,
    controlled_decrement, counter_width,
)

MAX_TRIES = 800

# T1 e_range extends to 5 so the deduplicated spec space comfortably
# exceeds the frozen-set tier quota (n=4 admits only ~31 distinct graphs
# with 3-4 edges).
TIER_PARAMS = {
    1: dict(n_choices=[4], e_range=(3, 5)),
    2: dict(n_choices=[5], e_range=(4, 6)),
    3: dict(n_choices=[6], e_range=(6, 10)),
    # T3p: zero-slack rolling (shared edge flag + edge counter + weight
    # counter); T4: scale-up within n + E + w <= 20
    4: dict(n_choices=[5, 6], e_range=(6, 9), rolling=True),
    5: dict(n_choices=[7, 8], e_range=(6, 8)),
}


class VertexCoverGenerator(TaskGenerator):
    family = "vertex_cover"
    tiers = (1, 2, 3, 4, 5)

    def generate(self, tier: int, seed: int) -> TaskInstance:
        params = TIER_PARAMS[tier]
        for sub in range(MAX_TRIES):
            rng = random.Random(stable_rng_seed(self.family, tier, seed, sub))
            n = rng.choice(params["n_choices"])
            lo, hi = params["e_range"]
            e = rng.randint(lo, min(hi, n * (n - 1) // 2))
            edges = sorted(rng.sample(list(itertools.combinations(range(n), 2)), e))
            touched = {u for edge in edges for u in edge}
            if len(touched) < n:
                self._record_reject(tier, seed, sub, "isolated_vertex")
                continue
            k = rng.randint(2, n - 2)
            w = counter_width(n)
            rolling = params.get("rolling", False)
            budget = (n + 1 + counter_width(e) + w) if rolling \
                else (n + e + w)
            if budget > GLOBAL_QUBIT_CAP:
                self._record_reject(tier, seed, sub, f"budget:{budget}")
                continue
            spec = {"n_vertices": n, "edges": [list(t) for t in edges],
                    "k": k, "encoding": "rolling" if rolling else "flags"}
            inst = TaskInstance(
                task_id=f"vertex_cover-{tier_label(tier)}-s{seed:04d}",
                family=self.family, tier=tier, seed=seed,
                problem_text="", formal_spec=spec,
                n_problem_qubits=n,
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
        raise RuntimeError(f"vertex_cover T{tier} s{seed}: retries exhausted")

    def classical_solutions(self, inst: TaskInstance) -> set[int]:
        n = inst.formal_spec["n_vertices"]
        edges = inst.formal_spec["edges"]
        k = inst.formal_spec["k"]
        sols = set()
        for x in range(1 << n):
            if bin(x).count("1") > k:
                continue
            if all((x >> a) & 1 or (x >> b) & 1 for a, b in edges):
                sols.add(x)
        return sols

    def reference_oracle(self, inst: TaskInstance) -> QuantumCircuit:
        n = inst.formal_spec["n_vertices"]
        edges = inst.formal_spec["edges"]
        k = inst.formal_spec["k"]
        e = len(edges)
        w = counter_width(n)

        if inst.formal_spec.get("encoding") == "rolling":
            # zero-slack: shared edge flag rolls into an edge counter;
            # the weight counter increments directly off the vertex qubits
            w_e = counter_width(e)
            qc = QuantumCircuit(n + 1 + w_e + w)
            flag = n
            cnt_e = list(range(n + 1, n + 1 + w_e))
            cnt_n = list(range(n + 1 + w_e, n + 1 + w_e + w))

            def edge_flag(j):
                a, b = edges[j]
                qc.x(flag)
                flag_on_pattern(qc, [a, b], [0, 0], flag)   # flag = a OR b

            for j in range(e):
                edge_flag(j)
                controlled_increment(qc, [flag], cnt_e)
                edge_flag(j)
            for i in range(n):
                controlled_increment(qc, [i], cnt_n)
            for t in range(k + 1):
                phase_on_pattern(
                    qc, cnt_e + cnt_n,
                    [(e >> i) & 1 for i in range(w_e)]
                    + [(t >> i) & 1 for i in range(w)])
            for i in range(n):
                controlled_decrement(qc, [i], cnt_n)
            for j in reversed(range(e)):
                edge_flag(j)
                controlled_decrement(qc, [flag], cnt_e)
                edge_flag(j)
            return qc

        qc = QuantumCircuit(n + e + w)
        flags = list(range(n, n + e))
        counter = list(range(n + e, n + e + w))

        def compute_edge_flags():
            for j, (a, b) in enumerate(edges):
                qc.x(flags[j])
                flag_on_pattern(qc, [a, b], [0, 0], flags[j])  # flag = a OR b

        compute_edge_flags()
        for i in range(n):
            controlled_increment(qc, [i], counter)
        # phase -1 when all edges covered AND weight == t for some t <= k
        for t in range(k + 1):
            phase_on_pattern(qc, flags + counter,
                             [1] * e + [(t >> i) & 1 for i in range(w)])
        for i in range(n):
            controlled_decrement(qc, [i], counter)
        compute_edge_flags()                       # involution
        return qc


# ---- problem-text rendering -------------------------------------------------

def render_verbose(spec: dict) -> str:
    n, edges, k = spec["n_vertices"], spec["edges"], spec["k"]
    return "\n".join([
        f"We have an undirected graph with {n} vertices (numbered 0..{n-1}) "
        f"and {len(edges)} edges:",
        "  edges = " + ", ".join(f"({a},{b})" for a, b in edges),
        "",
        "A vertex cover is a set S of vertices such that every edge has at "
        "least one endpoint in S.",
        "Qubit i (problem_qubits[i]) encodes whether vertex i is in S "
        "(1 = in the cover).",
        "",
        f"The classical predicate is f(x) = 1 if and only if x describes a "
        f"vertex cover of size at most k = {k} (i.e. every edge is covered "
        f"AND the number of 1-bits in x is <= {k}).",
    ])


def render_terse(spec: dict) -> str:
    return (f"Vertex cover, n={spec['n_vertices']}, edges={spec['edges']}, "
            f"k={spec['k']}. Qubit i = vertex i in cover. f(x)=1 iff every "
            f"edge has an endpoint with bit 1 and popcount(x) <= {spec['k']}.")
