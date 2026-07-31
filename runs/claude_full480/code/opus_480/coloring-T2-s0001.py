from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

    def qbits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # For each edge, an ancilla that computes "same color" (edge violated).
    # colors equal iff decoded colors match. Decoding: c=3 -> color 0 too.
    # We compute per-edge a flag = 1 iff same color, stored on a dedicated ancilla.
    # Then f = AND over edges of (NOT same_color) = all edges differ.
    # phase -1 iff f == 1.

    edge_anc = ancilla_qubits[:len(edges)]      # 5 ancillas, one per edge
    work = ancilla_qubits[len(edges)]           # 1 shared work ancilla

    # helper: for vertex v, produce controls describing decoded color.
    # decoded color equalities we need: for a given pair (u,w), same color iff
    # colors(u)==colors(w). Colors take values {0,1,2}. Codes: 00->0,01->1,10->2,11->0.
    # It's easier to test equality of decoded colors directly by enumerating the
    # (code_u, code_w) pairs that decode to equal colors and OR them.
    #
    # equal-color code pairs (cu,cw) with decode(cu)==decode(cw):
    # color0 codes: {0,3}; color1: {1}; color2: {2}
    # equal pairs: both in {0,3}  OR both ==1 OR both ==2.
    # We'll compute, per edge, the "same" flag via multi-controlled X on each pair,
    # toggling edge ancilla for every matching (cu,cw) combination.

    # code bits for vertex: (b0,b1). code value = b0 + 2 b1.
    # membership predicates:
    #   in{0,3}: (b0==b1)   -> both 0 or both 1
    #   ==1: b0=1,b1=0
    #   ==2: b0=0,b1=1
    #
    # For "same color" = (u in{0,3} AND w in{0,3}) OR (u==1 AND w==1) OR (u==2 AND w==2)
    #
    # (u in{0,3} AND w in{0,3}) itself is an OR over code combos; simplest is to
    # enumerate the exact code pairs. Equal-color code pairs:
    #   (0,0),(0,3),(3,0),(3,3),(1,1),(2,2)
    equal_pairs = [(0, 0), (0, 3), (3, 0), (3, 3), (1, 1), (2, 2)]

    def set_code(v, code, invert):
        # apply X so that the code bits become all-1 when vertex v has `code`.
        # code bit b0 = code&1, b1 = (code>>1)&1. To control on value, put X on
        # bits whose desired value is 0.
        b0, b1 = qbits(v)
        want0 = code & 1
        want1 = (code >> 1) & 1
        ops = []
        if want0 == 0:
            ops.append(b0)
        if want1 == 0:
            ops.append(b1)
        for q in ops:
            qc.x(q)
        return ops

    def compute_edge(u, w, target):
        b0u, b1u = qbits(u)
        b0w, b1w = qbits(w)
        controls = [b0u, b1u, b0w, b1w]
        for (cu, cw) in equal_pairs:
            ou = set_code(u, cu, False)
            ow = set_code(w, cw, False)
            qc.mcx(controls, target)
            for q in ow:
                qc.x(q)
            for q in ou:
                qc.x(q)

    # Compute all edge "same" flags
    for i, (u, w) in enumerate(edges):
        compute_edge(u, w, edge_anc[i])

    # f = 1 iff all edge flags are 0. Phase -1 on that state.
    # Flip all edge flags so "all zero originally" -> "all one now", then
    # multi-controlled Z (via mcp pi) onto work using edge flags as controls.
    for a in edge_anc:
        qc.x(a)
    # apply phase -1 when all edge_anc (now flipped) are 1
    qc.h(work)
    qc.mcx(edge_anc, work)
    qc.h(work)
    # Actually implement controlled-Z phase: use mcp
    # (the H-MCX-H above realizes an MCX, not a pure phase). Replace with phase.
    # Undo the accidental MCX:
    qc.h(work)
    qc.mcx(edge_anc, work)
    qc.h(work)
    # Now apply the true phase using mcp (multi-controlled phase) with pi.
    from qiskit.circuit.library import MCPhaseGate  # noqa
    qc.mcp(np.pi, edge_anc[:-1], edge_anc[-1])
    for a in edge_anc:
        qc.x(a)

    # Uncompute all edge "same" flags (mirror)
    for i in reversed(range(len(edges))):
        u, w = edges[i]
        compute_edge(u, w, edge_anc[i])
