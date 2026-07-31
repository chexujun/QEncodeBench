from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 3), (2, 3), (3, 4)]

    def vqubits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_anc = ancilla_qubits[:len(edges)]   # one per edge: 1 if edge OK (differ)
    flag = ancilla_qubits[len(edges)]        # AND of all edges

    def color_equal_terms(u, v, target):
        # Mark 'target' (flip) for each basis state where decoded(u)==decoded(v).
        # decoded maps: 00->0, 01->1, 10->2, 11->0.
        # Equal iff the (u,v) code pair is one of:
        #   both decode 0: {00,11} x {00,11}  -> 4 combos
        #   both decode 1: 01 & 01            -> 1 combo
        #   both decode 2: 10 & 10            -> 1 combo
        u0, u1 = vqubits(u)
        v0, v1 = vqubits(v)
        color0_codes = [(0, 0), (1, 1)]       # (b0,b1)
        color1_codes = [(1, 0)]
        color2_codes = [(0, 1)]
        classes = [color0_codes, color1_codes, color2_codes]
        for cls in classes:
            for (ub0, ub1) in cls:
                for (vb0, vb1) in cls:
                    controls = [u0, u1, v0, v1]
                    patt = [ub0, ub1, vb0, vb1]
                    for q, bit in zip(controls, patt):
                        if bit == 0:
                            qc.x(q)
                    qc.mcx(controls, target)
                    for q, bit in zip(controls, patt):
                        if bit == 0:
                            qc.x(q)

    # Compute edge ancillas: set to 1 when edge endpoints EQUAL, then flip to
    # get 1 = OK (differ).
    for i, (u, v) in enumerate(edges):
        color_equal_terms(u, v, edge_anc[i])
        qc.x(edge_anc[i])   # now edge_anc[i] == 1 iff colors differ (edge OK)

    # flag = AND of all edge_anc (all edges OK)
    qc.mcx(edge_anc, flag)

    # phase
    qc.z(flag)

    # uncompute
    qc.mcx(edge_anc, flag)
    for i, (u, v) in enumerate(edges):
        qc.x(edge_anc[i])
        color_equal_terms(u, v, edge_anc[i])
