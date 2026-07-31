from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (1, 2), (1, 3), (1, 4)]

    def vq(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    n_edges = len(edges)
    edge_anc = ancilla_qubits[:n_edges]   # one ancilla per edge: 1 iff edge OK (colors differ)
    final = ancilla_qubits[n_edges]        # AND of all edge_anc

    def decode_equal_compute(u, v, target):
        # Set target=1 iff decoded_color(u) == decoded_color(v).
        # decode: c=3 -> 0, else c. So color(u)==color(v) over {0,1,2,3->0}.
        # Equivalent: map codes to colors and compare. We enumerate the 4 "equal color" pairs
        # for each color using multi-controlled X on the two 2-qubit codes.
        u0, u1 = vq(u)
        v0, v1 = vq(v)
        ctrls = [u0, u1, v0, v1]
        # color(code): 00->0,01->1,10->2,11->0
        code_to_color = {0: 0, 1: 1, 2: 2, 3: 0}
        # list codes grouped by color
        from collections import defaultdict
        groups = defaultdict(list)
        for code, col in code_to_color.items():
            groups[col].append(code)
        # For each color, for each ordered pair (cu in group, cv in group): mark
        for col, codes in groups.items():
            for cu in codes:
                for cv in codes:
                    # controls pattern: u code == cu, v code == cv
                    bits = [cu & 1, (cu >> 1) & 1, cv & 1, (cv >> 1) & 1]
                    # apply X to zero-controls
                    zeros = [ctrls[i] for i, b in enumerate(bits) if b == 0]
                    for z in zeros:
                        qc.x(z)
                    qc.mcx(ctrls, target)
                    for z in zeros:
                        qc.x(z)

    # Compute per-edge "equal" flags, then we want edge_anc = NOT equal (colors differ).
    for i, (u, v) in enumerate(edges):
        decode_equal_compute(u, v, edge_anc[i])
        qc.x(edge_anc[i])   # edge_anc = 1 iff colors differ (edge satisfied)

    # final = AND of all edge_anc
    qc.mcx(edge_anc, final)

    # phase
    qc.z(final)

    # uncompute final
    qc.mcx(edge_anc, final)

    # uncompute edge flags (mirror)
    for i, (u, v) in reversed(list(enumerate(edges))):
        qc.x(edge_anc[i])
        decode_equal_compute(u, v, edge_anc[i])
