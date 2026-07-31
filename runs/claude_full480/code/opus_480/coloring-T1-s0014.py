from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 3), (1, 4), (2, 3), (3, 4)]

    def code_qubits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_ancillas = ancilla_qubits[:len(edges)]
    phase_ancilla = ancilla_qubits[len(edges)]

    def same_color(u, v, target):
        # Colors are equal iff decode(cu) == decode(cv).
        # decode: 00->0, 01->1, 10->2, 11->0.
        # Equal-color pairs of codes (cu,cv):
        #   (00,00),(00,11),(11,00),(11,11)  -> color 0
        #   (01,01)                          -> color 1
        #   (10,10)                          -> color 2
        u0, u1 = code_qubits(u)
        v0, v1 = code_qubits(v)
        pats = [
            (0, 0, 0, 0), (0, 0, 1, 1), (1, 1, 0, 0), (1, 1, 1, 1),
            (0, 1, 0, 1),
            (1, 0, 1, 0),
        ]
        ctrls = [u0, u1, v0, v1]
        for a0, a1, b0, b1 in pats:
            bits = (a0, a1, b0, b1)
            flip = [ctrls[i] for i in range(4) if bits[i] == 0]
            for q in flip:
                qc.x(q)
            qc.mcx(ctrls, target)
            for q in flip:
                qc.x(q)

    # Compute: edge_ancilla[i] = 1 iff edge i is monochromatic.
    for i, (u, v) in enumerate(edges):
        same_color(u, v, edge_ancillas[i])

    # phase_ancilla = 1 iff NO edge is monochromatic (all edge ancillas are 0).
    for a in edge_ancillas:
        qc.x(a)
    qc.mcx(edge_ancillas, phase_ancilla)
    for a in edge_ancillas:
        qc.x(a)

    # Phase: -1 iff phase_ancilla == 1 (i.e. f(x) == 1).
    qc.z(phase_ancilla)

    # Uncompute phase_ancilla.
    for a in edge_ancillas:
        qc.x(a)
    qc.mcx(edge_ancillas, phase_ancilla)
    for a in edge_ancillas:
        qc.x(a)

    # Uncompute edge ancillas (mirror).
    for i in reversed(range(len(edges))):
        u, v = edges[i]
        same_color(u, v, edge_ancillas[i])
