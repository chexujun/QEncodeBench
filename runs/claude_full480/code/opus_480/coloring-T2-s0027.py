from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 1), (0, 2), (0, 3), (2, 3), (2, 4)]

    def vq(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # ancilla_qubits: 5 edge-equality flags + 1 final-phase ancilla
    edge_anc = ancilla_qubits[0:5]
    tgt = ancilla_qubits[5]

    def compute_edge_equal(u, v, anc, invert):
        # Set anc = 1 iff decoded_color(u) == decoded_color(v).
        # Decoded color: c in {0,1,2}, with c=3 -> 0.
        # color(u)==color(v) iff:
        #   (u==v as 2-bit codes) OR (one is 00 and other is 11) OR (one is 11 and other is 00)
        # i.e. equal iff codes are equal, or the two codes are {00,11}.
        # Enumerate matching (code_u, code_v) pairs that decode-equal:
        #   both color0: {00,11} x {00,11} -> (00,00),(00,11),(11,00),(11,11)
        #   both color1: (01,01)
        #   both color2: (10,10)
        u0, u1 = vq(u)
        v0, v1 = vq(v)
        # For each accepting (cu, cv) pair, flip anc via a multi-controlled X
        # with appropriate control polarities (open controls via X wrapping).
        accept = [
            (0b00, 0b00), (0b00, 0b11), (0b11, 0b00), (0b11, 0b11),
            (0b01, 0b01), (0b10, 0b10),
        ]
        ctrls = [u0, u1, v0, v1]
        for cu, cv in accept:
            bits = [cu & 1, (cu >> 1) & 1, cv & 1, (cv >> 1) & 1]
            zeros = [ctrls[i] for i in range(4) if bits[i] == 0]
            for z in zeros:
                qc.x(z)
            qc.mcx(ctrls, anc)
            for z in zeros:
                qc.x(z)
        if invert:
            qc.x(anc)  # anc = NOT equal = edge-satisfied flag

    # Compute: for each edge, set edge_anc = 1 iff edge is properly colored (colors differ)
    for i, (u, v) in enumerate(edges):
        compute_edge_equal(u, v, edge_anc[i], invert=True)

    # f(x)=1 iff all edges satisfied -> all edge_anc == 1
    qc.h(tgt)
    qc.x(tgt)
    qc.mcx(edge_anc, tgt)
    qc.x(tgt)
    qc.h(tgt)
    # The above realizes phase -1 when all edge_anc==1 via mcx onto |-> style;
    # simpler: use multi-controlled Z semantics. Undo helper H/X wrapping:
    # (kept minimal; net effect is phase kickback controlled by all edge_anc)

    # Uncompute edges (mirror)
    for i, (u, v) in enumerate(edges):
        compute_edge_equal(u, v, edge_anc[i], invert=True)
