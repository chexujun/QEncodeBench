from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 4), (1, 2), (1, 4), (2, 3), (2, 4)]

    def vq(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_ancillas = ancilla_qubits[:len(edges)]      # 5 ancillas, one per edge
    flag = ancilla_qubits[len(edges)]                # 1 flag ancilla

    def edge_same_color(u, v, target):
        # After decode: color(c) where c=3 maps to 0. So colors equal iff
        # (cu == cv) OR (cu,cv) is an unordered {0,3} pair (both -> color 0).
        # Set target=1 iff the two vertices have the SAME decoded color.
        u0, u1 = vq(u)
        v0, v1 = vq(v)
        # Enumerate the 2-bit code pairs (cu,cv) that decode to same color.
        # colors: c0->0, c1->1, c2->2, c3->0. Same-color pairs:
        #   both color0: (0,0),(0,3),(3,0),(3,3)
        #   both color1: (1,1)
        #   both color2: (2,2)
        same_pairs = [(0, 0), (0, 3), (3, 0), (3, 3), (1, 1), (2, 2)]
        for cu, cv in same_pairs:
            controls = []
            zeros = []
            # cu bits: b0=cu&1, b1=(cu>>1)&1
            for (qb, bit) in [(u0, cu & 1), (u1, (cu >> 1) & 1),
                              (v0, cv & 1), (v1, (cv >> 1) & 1)]:
                controls.append(qb)
                zeros.append(bit)
            # Flip qubits whose desired control value is 0, so an all-1 MCX
            # triggers exactly on this code pair.
            for qb, bit in zip(controls, zeros):
                if bit == 0:
                    qc.x(qb)
            qc.mcx(controls, target)
            for qb, bit in zip(controls, zeros):
                if bit == 0:
                    qc.x(qb)

    # Compute: edge_ancillas[i] = 1 iff edge i is monochromatic (bad).
    for i, (u, v) in enumerate(edges):
        edge_same_color(u, v, edge_ancillas[i])

    # flag = 1 iff ALL edges are properly colored, i.e. all edge_ancillas == 0.
    # f(x)=1 iff no monochromatic edge. Compute flag via all-zero-controlled MCX.
    for a in edge_ancillas:
        qc.x(a)
    qc.mcx(edge_ancillas, flag)
    for a in edge_ancillas:
        qc.x(a)

    # Phase: -1 iff flag == 1 (i.e. f(x)=1).
    qc.z(flag)

    # Uncompute flag.
    for a in edge_ancillas:
        qc.x(a)
    qc.mcx(edge_ancillas, flag)
    for a in edge_ancillas:
        qc.x(a)

    # Uncompute edge ancillas (mirror).
    for i, (u, v) in enumerate(edges):
        edge_same_color(u, v, edge_ancillas[i])
