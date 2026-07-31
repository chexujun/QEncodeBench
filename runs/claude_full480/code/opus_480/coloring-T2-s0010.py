import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (1, 2), (1, 3), (1, 4), (2, 4)]

    def qubits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # edge-satisfied ancillas: one per edge, set to 1 when the edge's two
    # endpoints have DIFFERENT decoded colors.
    edge_anc = ancilla_qubits[:len(edges)]      # 5 ancillas
    final_anc = ancilla_qubits[len(edges)]      # 1 ancilla

    def decode_equal_compute(u, v, target):
        # Set `target` ^= 1 iff decoded_color(u) == decoded_color(v).
        # Decoded colors: c=0/3 -> 0, c=1 -> 1, c=2 -> 2.
        # Colors equal iff both codes decode to same color. We enumerate the
        # matching (code_u, code_v) pairs and toggle target for each via an
        # mcx over the 4 endpoint qubits with appropriate X masks.
        u0, u1 = qubits(u)
        v0, v1 = qubits(v)
        qb = [u0, u1, v0, v1]

        # decode map: code -> color
        def color(c):
            return {0: 0, 1: 1, 2: 2, 3: 0}[c]

        pairs = []
        for cu in range(4):
            for cv in range(4):
                if color(cu) == color(cv):
                    pairs.append((cu, cv))

        for cu, cv in pairs:
            bits = [cu & 1, (cu >> 1) & 1, cv & 1, (cv >> 1) & 1]
            # apply X to qubits whose required control value is 0
            flip = [qb[i] for i in range(4) if bits[i] == 0]
            for q in flip:
                qc.x(q)
            qc.mcx(qb, target)
            for q in flip:
                qc.x(q)

    def edge_diff_compute(u, v, target):
        # target starts |0>; we want target = 1 iff colors DIFFER.
        # Compute equal-flag into target, then X to invert -> differ-flag.
        decode_equal_compute(u, v, target)
        qc.x(target)

    def edge_diff_uncompute(u, v, target):
        qc.x(target)
        decode_equal_compute(u, v, target)

    # compute all edge-diff flags
    for (u, v), a in zip(edges, edge_anc):
        edge_diff_compute(u, v, a)

    # phase -1 iff ALL edge flags are 1
    qc.h(final_anc)
    qc.x(final_anc)
    qc.mcx(edge_anc, final_anc)
    qc.x(final_anc)
    qc.h(final_anc)

    # uncompute edge-diff flags
    for (u, v), a in zip(edges, edge_anc):
        edge_diff_uncompute(u, v, a)
