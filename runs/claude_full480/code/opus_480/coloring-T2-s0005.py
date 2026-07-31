from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 1), (0, 3), (1, 2), (1, 3), (3, 4)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_ancillas = ancilla_qubits[:5]
    final_anc = ancilla_qubits[5]

    def edge_diff_compute(u, v, anc):
        # anc = 1 iff colors of u and v are EQUAL (after surjective decode 11->0)
        u0, u1 = qb(u)
        v0, v1 = qb(v)
        # color(u)==color(v) iff decode(cu)==decode(cv).
        # decode maps: 00->0, 11->0, 01->1, 10->2.
        # Equal color cases (cu,cv):
        #   both color0: cu in {00,11}, cv in {00,11}
        #   both color1: cu=01, cv=01
        #   both color2: cu=10, cv=10
        # We set anc via OR of these disjoint patterns using mcx with controls.
        # color0(v): code 00 or 11 -> (u0==u1). Use a helper ancilla? Avoid; enumerate directly.
        # Enumerate the (cu,cv) 4x4 equal pairs: (00,00),(00,11),(11,00),(11,11),(01,01),(10,10)
        pairs = [
            ((0, 0), (0, 0)),
            ((0, 0), (1, 1)),
            ((1, 1), (0, 0)),
            ((1, 1), (1, 1)),
            ((1, 0), (1, 0)),  # code 01: b0=1,b1=0
            ((0, 1), (0, 1)),  # code 10: b0=0,b1=1
        ]
        for (a0, a1), (b0, b1) in pairs:
            flips = []
            if a0 == 0:
                qc.x(u0); flips.append(u0)
            if a1 == 0:
                qc.x(u1); flips.append(u1)
            if b0 == 0:
                qc.x(v0); flips.append(v0)
            if b1 == 0:
                qc.x(v1); flips.append(v1)
            qc.mcx([u0, u1, v0, v1], anc)
            for q in flips:
                qc.x(q)

    # Compute: edge_anc[i] = 1 iff edge i is monochromatic (violated)
    for i, (u, v) in enumerate(edges):
        edge_diff_compute(u, v, edge_ancillas[i])

    # final_anc = 1 iff NO edge violated (all edges proper) = AND of (not edge_anc)
    for a in edge_ancillas:
        qc.x(a)
    qc.mcx(edge_ancillas, final_anc)
    for a in edge_ancillas:
        qc.x(a)

    # Phase
    qc.z(final_anc)

    # Uncompute
    for a in edge_ancillas:
        qc.x(a)
    qc.mcx(edge_ancillas, final_anc)
    for a in edge_ancillas:
        qc.x(a)

    for i, (u, v) in enumerate(reversed(edges)):
        edge_diff_compute(u, v, edge_ancillas[len(edges) - 1 - i])
