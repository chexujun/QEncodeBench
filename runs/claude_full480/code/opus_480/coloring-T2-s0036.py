from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 4), (1, 2), (2, 3), (2, 4), (3, 4)]

    def vq(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # Ancillas: one per edge (6) to hold "edge is monochromatic" flag,
    # plus 1 spare used as scratch for the color-equality computation.
    edge_flags = ancilla_qubits[:6]
    scratch = ancilla_qubits[6]

    def color_equal_compute(u, w, flag):
        # decode: color(c) with c=3 -> 0. So color differs unless codes give
        # same decoded color. Decoded color classes:
        #   class0: codes 00(0) and 11(3)
        #   class1: code 01(1)
        #   class2: code 10(2)
        # Two vertices share a color iff same class.
        # We compute flag = 1 iff same decoded color, using scratch.
        ub0, ub1 = vq(u)
        wb0, wb1 = vq(w)

        # Compute predicate: same_color(u,w).
        # Enumerate matching (class,class) pairs via multi-controlled X onto flag,
        # controlling on exact code bit patterns for each matching combination.
        # class0 codes for a vertex: {00, 11}; class1: {01}; class2: {10}.
        # Matching combos (codeU, codeW):
        #   both class0: (00,00),(00,11),(11,00),(11,11)
        #   both class1: (01,01)
        #   both class2: (10,10)
        combos = [
            ((0, 0), (0, 0)),
            ((0, 0), (1, 1)),
            ((1, 1), (0, 0)),
            ((1, 1), (1, 1)),
            ((1, 0), (1, 0)),  # code 01: b0=1,b1=0
            ((0, 1), (0, 1)),  # code 10: b0=0,b1=1
        ]
        ctrls = [ub0, ub1, wb0, wb1]
        for (u0, u1), (w0, w1) in combos:
            pattern = [u0, u1, w0, w1]
            for bit, q in zip(pattern, ctrls):
                if bit == 0:
                    qc.x(q)
            qc.mcx(ctrls, flag)
            for bit, q in zip(pattern, ctrls):
                if bit == 0:
                    qc.x(q)

    # Compute all edge flags
    for (u, w), flag in zip(edges, edge_flags):
        color_equal_compute(u, w, flag)

    # f(x) = 1 iff NO edge is monochromatic, i.e. all edge_flags == 0.
    # Phase -1 when all flags are 0: sandwich with X on all flags, multi-controlled Z.
    for flag in edge_flags:
        qc.x(flag)
    # multi-controlled Z on all edge flags using scratch-free mcp
    qc.h(edge_flags[-1])
    qc.mcx(edge_flags[:-1], edge_flags[-1])
    qc.h(edge_flags[-1])
    for flag in edge_flags:
        qc.x(flag)

    # Uncompute all edge flags (mirror)
    for (u, w), flag in reversed(list(zip(edges, edge_flags))):
        color_equal_compute(u, w, flag)
