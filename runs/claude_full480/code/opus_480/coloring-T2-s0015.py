from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 3), (0, 4), (1, 2), (1, 4), (2, 4)]

    def vbits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_anc = ancilla_qubits[:len(edges)]      # 6 ancillas, one per edge
    flag = ancilla_qubits[len(edges)]           # final flag ancilla

    def edge_same(u, v, target):
        # set target ^= 1 iff decoded colors of u and v are equal.
        # colors: c in {0,1,2}, with code 3 -> color 0.
        # decoded color equal iff:
        #   both are color 0  (code 00 or 11), OR
        #   codes are exactly equal and code in {01,10}.
        # Equivalent: equal color iff
        #   (both codeVal maps to 0) OR (u0==v0 and u1==v1 and code is 01 or 10)
        # We enumerate the 4x4=16 pairs that give equal color and mark them.
        u0, u1 = vbits(u)
        v0, v1 = vbits(v)
        # color(u)==color(v) pairs (code_u, code_v):
        # color0 codes: {00,11}; color1: {01}; color2: {10}
        equal_pairs = [
            (0b00, 0b00), (0b00, 0b11), (0b11, 0b00), (0b11, 0b11),  # both color0
            (0b01, 0b01),  # both color1
            (0b10, 0b10),  # both color2
        ]
        for cu, cv in equal_pairs:
            bits = [
                (u0, cu & 1), (u1, (cu >> 1) & 1),
                (v0, cv & 1), (v1, (cv >> 1) & 1),
            ]
            ctrls = []
            for q, b in bits:
                if b == 0:
                    qc.x(q)
                ctrls.append(q)
            qc.mcx(ctrls, target)
            for q, b in bits:
                if b == 0:
                    qc.x(q)

    # compute: each edge ancilla = 1 iff that edge is monochromatic (bad)
    for (u, v), anc in zip(edges, edge_anc):
        edge_same(u, v, anc)

    # flag = 1 iff ALL edge ancillas are 0 (i.e. all edges properly colored)
    for anc in edge_anc:
        qc.x(anc)
    qc.mcx(edge_anc, flag)
    for anc in edge_anc:
        qc.x(anc)

    # phase: -1 iff flag == 1 (a valid coloring)
    qc.z(flag)

    # uncompute flag
    for anc in edge_anc:
        qc.x(anc)
    qc.mcx(edge_anc, flag)
    for anc in edge_anc:
        qc.x(anc)

    # uncompute edge ancillas (mirror)
    for (u, v), anc in zip(edges, edge_anc):
        edge_same(u, v, anc)
