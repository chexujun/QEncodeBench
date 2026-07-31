from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (0, 3), (1, 2)]

    def vq(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # ancilla layout: one "edge OK" ancilla per edge, plus a final flag ancilla
    edge_anc = ancilla_qubits[:len(edges)]
    flag = ancilla_qubits[len(edges)]

    def decode_equal_compute(u, v, target):
        # set target = 1 iff decoded(u) == decoded(v)
        # decoded colors: c in {0,1,2}, with code 3 -> 0.
        # colors equal iff codes map to same color. Enumerate matching code pairs:
        # color0 codes: {00(0), 11(3)}, color1: {01(1)}, color2: {10(2)}
        au0, au1 = vq(u)
        av0, av1 = vq(v)
        # For each pair (cu, cv) with same decoded color, flip target via multi-control.
        color_codes = {0: [(0, 0), (1, 1)], 1: [(1, 0)], 2: [(0, 1)]}
        for color, codes in color_codes.items():
            for (u0, u1) in codes:
                for (v0, v1) in codes:
                    ctrls = [au0, au1, av0, av1]
                    vals = [u0, u1, v0, v1]
                    for q, b in zip(ctrls, vals):
                        if b == 0:
                            qc.x(q)
                    qc.mcx(ctrls, target)
                    for q, b in zip(ctrls, vals):
                        if b == 0:
                            qc.x(q)

    # compute each edge_anc = 1 iff endpoints SAME color (bad)
    for (u, v), ea in zip(edges, edge_anc):
        decode_equal_compute(u, v, ea)

    # flag = 1 iff all edges OK (no edge same-colored): edge_anc all 0
    for ea in edge_anc:
        qc.x(ea)
    qc.mcx(edge_anc, flag)
    for ea in edge_anc:
        qc.x(ea)

    # phase
    qc.z(flag)

    # uncompute flag
    for ea in edge_anc:
        qc.x(ea)
    qc.mcx(edge_anc, flag)
    for ea in edge_anc:
        qc.x(ea)

    # uncompute edge_anc (mirror)
    for (u, v), ea in reversed(list(zip(edges, edge_anc))):
        decode_equal_compute(u, v, ea)
