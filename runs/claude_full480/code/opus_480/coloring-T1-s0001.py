import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (2, 3), (2, 4), (3, 4)]

    def vqubits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # For each edge, compute an ancilla = 1 iff the two endpoints have the
    # SAME color, then the predicate f=1 iff NO edge is monochromatic, i.e.
    # all edge-ancillas are 0.  Phase -1 when all edge-ancillas are |0>.
    #
    # Colors (surjective decode): code c in {0,1,2,3}, color = c if c<3 else 0.
    # So color(u)==color(v) iff:
    #   both codes in {0,3} (color 0), or codes equal to 1, or codes equal to 2.
    # Equivalently color 0 set = {00, 11}, color1 = {01}, color2 = {10}.
    #
    # We build, per edge, an ancilla = OR over the 3 colors of
    # (u in color k AND v in color k).  Since colors partition, at most one
    # term is 1, so we can just add (CX-style via ccx) the three terms.

    edge_anc = ancilla_qubits  # one ancilla per edge (4 edges, >=4 ancillas)

    def color_match_compute(u0, u1, v0, v1, anc):
        # color0: code in {00,11}  <=> (u0==u1). indicator = XNOR(u0,u1) for u,
        #   and XNOR(v0,v1) for v, then AND.
        # We need temp storage; use two problem-independent temp ancillas.
        # Instead, expand each color separately with mcx over literal patterns.
        #
        # color k membership as product of literals:
        #   color0 for a vertex = {00, 11}: not a single product; handle as two.
        # To keep it a clean product-of-literals per basis pattern, enumerate
        # the (u_pattern, v_pattern) code-pairs that are monochromatic and add
        # a multi-controlled X for each. This is NOT enumerating solutions of
        # f; it enumerates the fixed 2-qubit-per-vertex code equalities that
        # define the SAME-color relation (a fixed 4-input boolean function of
        # the edge's 4 qubits), independent of graph size.

        # same-color code pairs (cu, cv) with color(cu)==color(cv):
        same_pairs = []
        for cu in range(4):
            for cv in range(4):
                col_u = cu if cu < 3 else 0
                col_v = cv if cv < 3 else 0
                if col_u == col_v:
                    same_pairs.append((cu, cv))

        controls = [u0, u1, v0, v1]
        for (cu, cv) in same_pairs:
            bits = [cu & 1, (cu >> 1) & 1, cv & 1, (cv >> 1) & 1]
            # set X on zero-controls
            flips = [controls[i] for i in range(4) if bits[i] == 0]
            for q in flips:
                qc.x(q)
            qc.mcx(controls, anc)
            for q in flips:
                qc.x(q)

    # compute all edge ancillas
    for e, (a, b) in enumerate(edges):
        au0, au1 = vqubits(a)
        bv0, bv1 = vqubits(b)
        color_match_compute(au0, au1, bv0, bv1, edge_anc[e])

    # phase: -1 iff all edge ancillas == 0.
    # Flip all edge ancillas, apply multi-controlled Z, flip back.
    ctrls = [edge_anc[e] for e in range(len(edges))]
    for q in ctrls:
        qc.x(q)
    # multi-controlled Z on the edge ancillas
    if len(ctrls) == 1:
        qc.z(ctrls[0])
    else:
        qc.h(ctrls[-1])
        qc.mcx(ctrls[:-1], ctrls[-1])
        qc.h(ctrls[-1])
    for q in ctrls:
        qc.x(q)

    # uncompute edge ancillas (mirror)
    for e in reversed(range(len(edges))):
        a, b = edges[e]
        au0, au1 = vqubits(a)
        bv0, bv1 = vqubits(b)
        color_match_compute(au0, au1, bv0, bv1, edge_anc[e])
