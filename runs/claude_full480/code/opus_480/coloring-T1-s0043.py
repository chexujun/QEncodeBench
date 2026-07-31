from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 2), (0, 3), (1, 3), (2, 3)]

    def vqubits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_anc = ancilla_qubits[:4]
    flag = ancilla_qubits[4]

    def edge_compute(u, w, anc):
        # anc <- 1 iff decoded_color(u) == decoded_color(w)
        # decode: c=0->0, 1->1, 2->2, 3->0 ; so color(u)==color(w) means
        # same decoded color. We compute "different" is easier via direct
        # comparison over the 4x4 code combos that are monochromatic.
        u0, u1 = vqubits(u)
        w0, w1 = vqubits(w)
        # Monochromatic code pairs (cu,cw): colors equal after decode.
        # decode map: 00->0,01->1,10->2,11->0
        # color0 codes: {00,11}; color1: {01}; color2: {10}
        mono = []
        groups = [[(0, 0), (1, 1)], [(0, 1)], [(1, 0)]]
        for g in groups:
            for cu in g:
                for cw in g:
                    mono.append((cu, cw))
        for (cu0, cu1), (cw0, cw1) in mono:
            controls = [u0, u1, w0, w1]
            neg = [cu0 == 0, cu1 == 0, cw0 == 0, cw1 == 0]
            for c, n in zip(controls, neg):
                if n:
                    qc.x(c)
            qc.mcx(controls, anc)
            for c, n in zip(controls, neg):
                if n:
                    qc.x(c)

    # compute each edge's "monochromatic" flag
    for (u, w), anc in zip(edges, edge_anc):
        edge_compute(u, w, anc)

    # f(x)=1 iff NO edge is monochromatic, i.e. all edge_anc == 0.
    # flag <- 1 iff all edge_anc are 0.
    for a in edge_anc:
        qc.x(a)
    qc.mcx(edge_anc, flag)
    for a in edge_anc:
        qc.x(a)

    # phase
    qc.z(flag)

    # uncompute flag
    for a in edge_anc:
        qc.x(a)
    qc.mcx(edge_anc, flag)
    for a in edge_anc:
        qc.x(a)

    # uncompute edge flags (mirror)
    for (u, w), anc in zip(reversed(edges), reversed(edge_anc)):
        edge_compute(u, w, anc)
