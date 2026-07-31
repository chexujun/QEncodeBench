import numpy as np
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 2), (0, 3), (1, 3)]

    def vqubits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # For each edge, ancilla e is set to 1 iff the two endpoints share the SAME color.
    # Colors: c=0->0, c=1->1, c=2->2, c=3->0. So "same color" means:
    #   (a0==b0 and a1==b1)  [codes equal]  OR
    #   one code is 00 and other is 11, or one is 11 and other is 00 (both color 0).
    # Equivalent: colors equal iff decode(u)==decode(v). Enumerate the 16 code pairs.
    # We compute same-color per edge into an edge ancilla, then require NO edge is
    # monochromatic: predicate f = AND over edges of (colors differ) = AND of NOT(same).
    # Mark f==1 with phase -1.

    edge_ancillas = [ancilla_qubits[i] for i in range(len(edges))]
    flag = ancilla_qubits[len(edges)]

    def same_color_compute(u, v, target):
        a0, a1 = vqubits(u)
        b0, b1 = vqubits(v)
        controls = [a0, a1, b0, b1]
        # decode(code): 00->0,01->1,10->2,11->0
        def dec(code):
            return {0: 0, 1: 1, 2: 2, 3: 0}[code]
        for ca in range(4):
            for cb in range(4):
                if dec(ca) == dec(cb):
                    pattern = [ca & 1, (ca >> 1) & 1, cb & 1, (cb >> 1) & 1]
                    for q, bit in zip(controls, pattern):
                        if bit == 0:
                            qc.x(q)
                    qc.mcx(controls, target)
                    for q, bit in zip(controls, pattern):
                        if bit == 0:
                            qc.x(q)

    # compute same-color ancillas
    for (u, v), ea in zip(edges, edge_ancillas):
        same_color_compute(u, v, ea)

    # f = AND of NOT(same_color). Flip edge ancillas so 1 means "colors differ".
    for ea in edge_ancillas:
        qc.x(ea)
    # flag = AND of (colors differ over all edges)
    qc.mcx(edge_ancillas, flag)
    qc.z(flag)
    qc.mcx(edge_ancillas, flag)
    for ea in edge_ancillas:
        qc.x(ea)

    # uncompute same-color ancillas (mirror)
    for (u, v), ea in zip(reversed(edges), reversed(edge_ancillas)):
        same_color_compute(u, v, ea)
