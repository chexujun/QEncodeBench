import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 4), (1, 2), (1, 3), (1, 4), (2, 4), (3, 4)]

    def qb(v):
        # (low bit, high bit) qubits for vertex v
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # edge_flags[k] ancilla = 1 iff edge k is SATISFIED (colors differ)
    edge_flags = ancilla_qubits[0:7]
    final = ancilla_qubits[7]

    def edge_diff_compute(u, v, flag):
        # Decode: color(u) != color(v) with 11 == 00 (color 0).
        # color map: 00->0, 01->1, 10->2, 11->0.
        # We compute predicate "same color" then invert to "different".
        # same color iff the two vertices decode to identical color.
        #
        # Build helper: mark equality using compute of intermediate.
        # We use a scratch approach: since only one ancilla (flag) is
        # available per edge here, compute via a small reversible routine
        # using the flag itself accumulating XOR of a boolean formula.
        #
        # color equality is not a simple XOR because of the 11->0 alias.
        # Enumerate SAME-color code pairs:
        #   color0 codes: {00, 11}; color1: {01}; color2: {10}
        # same iff (both in {00,11}) or (both ==01) or (both ==10).
        #
        # We instead directly set flag = 1 when DIFFERENT.
        # Strategy: set flag=1 initially, then subtract (toggle to 0) the
        # SAME-color cases via multi-controlled X onto flag.
        u0, u1 = qb(u)
        v0, v1 = qb(v)
        qc.x(flag)  # assume different

        # helper: is vertex color 0 (code 00 or 11) — controlled ops need
        # ancilla-free formulation. We implement each "same" case as an
        # MCX whose controls encode exact codes, using X wrappers.

        # same == color1: u==01 and v==01  -> u0=1,u1=0,v0=1,v1=0
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], flag)
        qc.x(u1); qc.x(v1)

        # same == color2: u==10 and v==10 -> u0=0,u1=1,v0=0,v1=1
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], flag)
        qc.x(u0); qc.x(v0)

        # same == color0: u in {00,11} and v in {00,11}
        # u in {00,11} means u0==u1 ; v in {00,11} means v0==v1.
        # Cases: (00,00),(00,11),(11,00),(11,11)
        for uc in (0, 1):      # uc: value of u0(=u1)
            for vc in (0, 1):
                wraps = []
                if uc == 0:
                    wraps += [u0, u1]
                if vc == 0:
                    wraps += [v0, v1]
                for w in wraps:
                    qc.x(w)
                qc.mcx([u0, u1, v0, v1], flag)
                for w in wraps:
                    qc.x(w)

    # compute all edge flags
    for k, (u, v) in enumerate(edges):
        edge_diff_compute(u, v, edge_flags[k])

    # final = AND of all edge flags
    qc.mcx(edge_flags, final)
    qc.z(final)
    qc.mcx(edge_flags, final)

    # uncompute edge flags (mirror)
    for k in range(len(edges) - 1, -1, -1):
        u, v = edges[k]
        edge_diff_compute(u, v, edge_flags[k])
