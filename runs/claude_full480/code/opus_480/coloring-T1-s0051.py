from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 2), (0, 4), (1, 3), (2, 4)]

    def q(v, b):
        return problem_qubits[2 * v + b]

    # For each edge, an ancilla holds 1 iff the two endpoints have the SAME color.
    # f(x) = 1 iff ALL edges are properly colored, i.e. NO edge is monochromatic,
    # i.e. all edge-ancillas are 0.
    edge_anc = [ancilla_qubits[i] for i in range(len(edges))]
    flag = ancilla_qubits[len(edges)]

    def color_a(v):
        return q(v, 0)

    def color_b(v):
        return q(v, 1)

    # Compute "same color" for an edge (u,w) into ancilla `a`.
    # Colors: c=0 (00), c=1 (01), c=2 (10), c=3 (11)->color 0.
    # Two vertices are the same color iff:
    #   both are color 0: c in {00,11} for both, OR
    #   both color 1: 01 & 01, OR
    #   both color 2: 10 & 10.
    # color0(v) = (b0==b1)  = NOT (b0 XOR b1)
    # color1(v) = b0 AND NOT b1
    # color2(v) = NOT b0 AND b1
    #
    # same(u,w) = color0(u)&color0(w) OR color1(u)&color1(w) OR color2(u)&color2(w)
    #
    # We compute each color-match term into `a` via MCX with appropriate X-conditioning,
    # using temporary scratch on the flag qubit is not needed; we OR by XOR-ing terms
    # since the three terms are mutually exclusive (a vertex has exactly one color),
    # so their contributions never both fire -> XOR == OR.

    def compute_same(u, w, a):
        u0, u1 = color_a(u), color_b(u)
        w0, w1 = color_a(w), color_b(w)

        # term color1: u0 & ~u1 & w0 & ~w1
        qc.x(u1); qc.x(w1)
        qc.mcx([u0, u1, w0, w1], a)
        qc.x(u1); qc.x(w1)

        # term color2: ~u0 & u1 & ~w0 & w1
        qc.x(u0); qc.x(w0)
        qc.mcx([u0, u1, w0, w1], a)
        qc.x(u0); qc.x(w0)

        # term color0: (u0==u1) & (w0==w1)
        # color0(v) true iff u0 XOR u1 == 0. Map: set a temporary equality.
        # (u0==u1) = ~(u0 XOR u1). Build via: flip so controls are 1 when equal.
        # Use CX to fold u1 into u0, w1 into w0: after, u0 holds u0^u1, w0 holds w0^w1.
        qc.cx(u1, u0)
        qc.cx(w1, w0)
        # now color0 iff u0==0 and w0==0
        qc.x(u0); qc.x(w0)
        qc.mcx([u0, w0], a)
        qc.x(u0); qc.x(w0)
        # uncompute the folding
        qc.cx(w1, w0)
        qc.cx(u1, u0)

    # Compute all edge "same" ancillas.
    for i, (u, w) in enumerate(edges):
        compute_same(u, w, edge_anc[i])

    # f = 1 iff all edge_anc == 0. Apply phase -1 on that condition.
    # Flip edge ancillas so "all proper" == all ones, then multi-controlled Z.
    for a in edge_anc:
        qc.x(a)
    # multi-controlled Z on all edge ancillas
    if len(edge_anc) == 1:
        qc.z(edge_anc[0])
    else:
        qc.h(edge_anc[-1])
        qc.mcx(edge_anc[:-1], edge_anc[-1])
        qc.h(edge_anc[-1])
    for a in edge_anc:
        qc.x(a)

    # Uncompute edge ancillas (mirror).
    for i in reversed(range(len(edges))):
        u, w = edges[i]
        compute_same(u, w, edge_anc[i])
