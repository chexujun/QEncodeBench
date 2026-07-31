import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 2), (0, 5), (1, 2), (1, 4), (2, 3), (2, 4), (3, 4), (4, 5)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_ancillas = ancilla_qubits[:len(edges)]
    flag = ancilla_qubits[len(edges)]

    def same_color_compute(u, v, anc):
        # Sets anc = 1 iff decoded_color(u) == decoded_color(v).
        # Colors: c=0->0, c=1->1, c=2->2, c=3->0. So color 0 <=> code in {00,11}.
        # Two vertices share a color iff:
        #   (both color0) OR (both code 01) OR (both code 10)
        # color0(v) = (b0==b1). code01 = b0 & ~b1. code10 = ~b0 & b1.
        u0, u1 = qb(u)
        v0, v1 = qb(v)

        # term A: both color 0  <=> (u0==u1) AND (v0==v1)
        # compute p = (u0==u1) into u-pair-parity ancilla? We must use provided ancillas only.
        # We'll build directly onto anc using a sequence of MCX with X-masks.
        # anc XOR= [both color0] XOR [both 01] XOR [both 10]
        # These three events are mutually exclusive, so XOR == OR here.

        # both color 0: (u0 XOR u1 == 0) and (v0 XOR v1 == 0).
        # Implement equality via controlling on matched patterns:
        #   u0==u1 has patterns (0,0) and (1,1); same for v. 4 combos -> 4 MCX.
        for uu in (0, 1):
            for vv in (0, 1):
                ctrls = [u0, u1, v0, v1]
                pattern = [uu, uu, vv, vv]
                for c, p in zip(ctrls, pattern):
                    if p == 0:
                        qc.x(c)
                qc.mcx(ctrls, anc)
                for c, p in zip(ctrls, pattern):
                    if p == 0:
                        qc.x(c)

        # both code 01 (b0=1,b1=0): u=(1,0), v=(1,0)
        ctrls = [u0, u1, v0, v1]
        pattern = [1, 0, 1, 0]
        for c, p in zip(ctrls, pattern):
            if p == 0:
                qc.x(c)
        qc.mcx(ctrls, anc)
        for c, p in zip(ctrls, pattern):
            if p == 0:
                qc.x(c)

        # both code 10 (b0=0,b1=1): u=(0,1), v=(0,1)
        pattern = [0, 1, 0, 1]
        for c, p in zip(ctrls, pattern):
            if p == 0:
                qc.x(c)
        qc.mcx(ctrls, anc)
        for c, p in zip(ctrls, pattern):
            if p == 0:
                qc.x(c)

    # Compute: each edge ancilla = 1 iff that edge is monochromatic (same color).
    for (u, v), anc in zip(edges, edge_ancillas):
        same_color_compute(u, v, anc)

    # f = 1 iff ALL edges are properly colored, i.e. NO edge ancilla is 1.
    # flag = 1 iff all edge_ancillas == 0. Flip ancillas, MCX, then phase.
    for anc in edge_ancillas:
        qc.x(anc)
    qc.mcx(edge_ancillas, flag)
    qc.z(flag)
    qc.mcx(edge_ancillas, flag)
    for anc in edge_ancillas:
        qc.x(anc)

    # Uncompute edge ancillas.
    for (u, v), anc in zip(edges, edge_ancillas):
        same_color_compute(u, v, anc)
