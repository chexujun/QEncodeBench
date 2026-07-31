from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (1, 3)]

    # Per vertex v: code bits (b0, b1) on problem_qubits[2v], problem_qubits[2v+1].
    # Decoding: c=0->0, 1->1, 2->2, 3->0. So color equals c except code 11 maps to 0.
    # Two vertices share a color iff their decoded colors are equal.
    #
    # Encode "same color" for an edge (u,v) into a per-edge ancilla, using two
    # extra scratch ancillas to build the decoded-color equality. Then the
    # predicate f = AND over edges of (colors differ) = NOT(any edge same).
    #
    # We compute for each edge an ancilla eq_e = 1 iff colors(u)==colors(v).
    # Then f=1 iff all eq_e==0, i.e. we want phase -1 when NOT(eq0 OR eq1 OR eq2).
    #
    # Strategy: compute all eq_e into 3 edge-ancillas, then apply a phase of -1
    # on the state where all eq_e == 0 (multi-controlled Z on zeros), then
    # uncompute the eq_e ancillas.
    #
    # We have 4 ancillas total. Edges = 3, so we need 3 edge-ancillas plus we
    # need scratch for computing each equality. We compute each eq_e using
    # scratch, uncompute the scratch immediately (reuse the 4th ancilla as
    # scratch), leaving only 3 edge-ancillas occupied. Then phase, then reverse.

    a_edge = ancilla_qubits[0:3]
    scratch = ancilla_qubits[3]

    def color_bits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # Helper: append operations that set eq (edge-ancilla) = 1 iff decoded
    # colors of u and v are equal. decoded color mapping over 2 bits (b0,b1):
    #   00->0, 01->1, 10->2, 11->0
    # Equal-color condition between (a0,a1) and (c0,c1):
    #   Let A = decode(a), C = decode(c). A==C.
    # We build it via the truth table on 4 bits. Equal iff one of:
    #   both decode to 0: a in {00,11} and c in {00,11}
    #   both ==1: a==01 and c==01
    #   both ==2: a==10 and c==10
    # We compute intermediate predicates into scratch and XOR into eq.
    #
    # It's cleanest to enumerate the (a,c) bit-combos that make eq=1 and, for
    # each, flip eq with a multi-controlled X conditioned on the exact 4-bit
    # pattern (using X gates to select zeros). This is NOT enumerating all
    # solutions of the whole problem; it's a fixed 4-input boolean gate per edge.

    def eq_pairs():
        # list of (a0,a1,c0,c1) with decode(a)==decode(c)
        pats = []
        for a0 in (0, 1):
            for a1 in (0, 1):
                da = {0: 0, 1: 1, 2: 2, 3: 0}[a0 + 2 * a1]
                for c0 in (0, 1):
                    for c1 in (0, 1):
                        dc = {0: 0, 1: 1, 2: 2, 3: 0}[c0 + 2 * c1]
                        if da == dc:
                            pats.append((a0, a1, c0, c1))
        return pats

    patterns = eq_pairs()

    def compute_eq(u, v, eq):
        a0, a1 = color_bits(u)
        c0, c1 = color_bits(v)
        controls = [a0, a1, c0, c1]
        for (p0, p1, q0, q1) in patterns:
            bits = [p0, p1, q0, q1]
            zeros = [controls[i] for i in range(4) if bits[i] == 0]
            for z in zeros:
                qc.x(z)
            qc.mcx(controls, eq)
            for z in zeros:
                qc.x(z)

    def uncompute_eq(u, v, eq):
        # same operation is its own inverse (each mcx toggles eq; applying the
        # identical sequence again returns eq to 0)
        compute_eq(u, v, eq)

    # Compute eq for each edge into its dedicated edge-ancilla.
    for e, (u, v) in enumerate(edges):
        compute_eq(u, v, a_edge[e])

    # Phase: -1 when predicate f==1, i.e. all eq_e == 0.
    # Flip edge-ancillas so the all-zero condition becomes all-one, then MCZ.
    for e in range(len(edges)):
        qc.x(a_edge[e])
    # multi-controlled Z on the 3 edge-ancillas
    if len(edges) == 1:
        qc.z(a_edge[0])
    else:
        qc.h(a_edge[-1])
        qc.mcx(a_edge[:-1], a_edge[-1])
        qc.h(a_edge[-1])
    for e in range(len(edges)):
        qc.x(a_edge[e])

    # Uncompute eq ancillas (reverse order).
    for e in reversed(range(len(edges))):
        u, v = edges[e]
        uncompute_eq(u, v, a_edge[e])
