from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 3), (1, 2), (3, 4)]

    def vqubits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # ancilla layout: a_edge[k] = 1 iff edge k is "same color" (bad).
    # We need f = 1 iff ALL edges are good (colors differ).
    # Strategy: compute per-edge "same color" flag into an edge ancilla,
    # then phase -1 iff all edge flags are 0 (all good), using an
    # X-wrapped multi-controlled Z on the edge flags.
    edge_anc = ancilla_qubits[:len(edges)]   # 3 ancillas for edge flags
    work = ancilla_qubits[len(edges)]        # 1 scratch ancilla

    def color_equal_flag(u, v, flag):
        # Set flag ^= 1 iff decoded_color(u) == decoded_color(v).
        # Codes: 00->0, 01->1, 10->2, 11->0.
        # color(u)==color(v) cases (unordered code pairs) where equal color:
        #   both color0: codes in {00,11} for each -> (00,00),(00,11),(11,00),(11,11)
        #   both color1: (01,01)
        #   both color2: (10,10)
        u0, u1 = vqubits(u)
        v0, v1 = vqubits(v)

        # We enumerate the (cu, cv) code pairs that decode to same color.
        # For each such pair, add 1 to flag via a multi-controlled X with
        # appropriate X-masks so control triggers exactly on that pair.
        same_pairs = []
        # color0 codes: {0b00, 0b11}; color1: {0b01}; color2: {0b10}
        color_codes = {0: [0b00, 0b11], 1: [0b01], 2: [0b10]}
        for codes in color_codes.values():
            for cu in codes:
                for cv in codes:
                    same_pairs.append((cu, cv))

        controls = [u0, u1, v0, v1]
        for (cu, cv) in same_pairs:
            bits = [cu & 1, (cu >> 1) & 1, cv & 1, (cv >> 1) & 1]
            # X-mask: flip qubits whose desired control value is 0
            for q, b in zip(controls, bits):
                if b == 0:
                    qc.x(q)
            qc.mcx(controls, flag)
            for q, b in zip(controls, bits):
                if b == 0:
                    qc.x(q)

    # compute edge flags
    for k, (u, v) in enumerate(edges):
        color_equal_flag(u, v, edge_anc[k])

    # phase: -1 iff all edge flags == 0 (all edges good)
    for f in edge_anc:
        qc.x(f)
    # multi-controlled Z on edge_anc: use H-mcx-H on last, or mcp(pi)
    qc.mcp(math.pi, edge_anc[:-1], edge_anc[-1])
    for f in edge_anc:
        qc.x(f)

    # uncompute edge flags (mirror)
    for k, (u, v) in reversed(list(enumerate(edges))):
        color_equal_flag(u, v, edge_anc[k])
