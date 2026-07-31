from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 1), (0, 2), (1, 3), (2, 3)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_anc = ancilla_qubits[:4]
    final_anc = ancilla_qubits[4]

    def edge_same_compute(v, w, anc):
        # anc becomes 1 iff decoded color of v == decoded color of w.
        # color(v)==color(w) iff codes equal OR one is 11 and other is 00
        # (since 11 and 00 both -> color 0), and codes 01,10 map uniquely.
        # Equivalent: colors equal iff (cv==cw) or ({cv,cw}=={00,11}).
        # Detect the "colors equal" predicate directly.
        a0, a1 = qb(v)
        b0, b1 = qb(w)
        # We enumerate the color-equal condition via helper ancilla-free logic
        # using controlled gates. colors equal cases (cv,cw):
        #   (00,00),(00,11),(11,00),(11,11) -> color0==color0
        #   (01,01) -> color1
        #   (10,10) -> color2
        # Build predicate p = OR of these mutually exclusive terms.
        # Term A: cv in {00,11} AND cw in {00,11}
        #   cv in {00,11} means a0==a1 ; cw in {00,11} means b0==b1
        # Term B: cv==01 and cw==01 -> a0=1,a1=0,b0=1,b1=0
        # Term C: cv==10 and cw==10 -> a0=0,a1=1,b0=0,b1=1
        # These three terms are mutually exclusive, so anc = A xor B xor C works.

        # Term A: a0==a1 and b0==b1.
        # a0==a1  <=> NOT(a0 xor a1). Use temp on anc via multi-controls with X wraps.
        # Flip a1 to represent (a0==a1) as a1'==... simpler: compute using X gates.
        # We toggle anc for pattern (a0==a1 AND b0==b1):
        # a0==a1 true when (a0,a1) in {(0,0),(1,1)}.
        # Use two mcx: one for (0,0,*) and one for (1,1,*) combos with b.
        # Sub-case (a0=0,a1=0,b0=0,b1=0)
        qc.x(a0); qc.x(a1); qc.x(b0); qc.x(b1)
        qc.mcx([a0, a1, b0, b1], anc)
        qc.x(a0); qc.x(a1); qc.x(b0); qc.x(b1)
        # (0,0,1,1)
        qc.x(a0); qc.x(a1)
        qc.mcx([a0, a1, b0, b1], anc)
        qc.x(a0); qc.x(a1)
        # (1,1,0,0)
        qc.x(b0); qc.x(b1)
        qc.mcx([a0, a1, b0, b1], anc)
        qc.x(b0); qc.x(b1)
        # (1,1,1,1)
        qc.mcx([a0, a1, b0, b1], anc)
        # Term B: (0,1,0,1) meaning a0=1,a1=0,b0=1,b1=0 -> wait 01 code means b0=1,b1=0
        # cv==01: a0=1,a1=0 ; cw==01: b0=1,b1=0
        qc.x(a1); qc.x(b1)
        qc.mcx([a0, a1, b0, b1], anc)
        qc.x(a1); qc.x(b1)
        # Term C: cv==10: a0=0,a1=1 ; cw==10: b0=0,b1=1
        qc.x(a0); qc.x(b0)
        qc.mcx([a0, a1, b0, b1], anc)
        qc.x(a0); qc.x(b0)

    # Compute each edge's "same color" flag into its ancilla.
    for i, (v, w) in enumerate(edges):
        edge_same_compute(v, w, edge_anc[i])

    # f(x)=1 iff NO edge is monochromatic, i.e. all edge_anc == 0.
    # final predicate = AND of (NOT edge_anc[i]). Flip all, mcx, phase, unflip.
    for a in edge_anc:
        qc.x(a)
    qc.h(final_anc)
    qc.mcx(edge_anc, final_anc)
    qc.h(final_anc)
    for a in edge_anc:
        qc.x(a)

    # Uncompute edge ancillas (mirror).
    for i, (v, w) in reversed(list(enumerate(edges))):
        edge_same_compute(v, w, edge_anc[i])
