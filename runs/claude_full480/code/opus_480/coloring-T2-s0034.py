from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits) -> None:
    edges = [(0, 1), (0, 3), (0, 4), (1, 2), (1, 3), (2, 3), (2, 4), (3, 4)]

    def qb(v):
        # (low, high) qubits for vertex v
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_anc = ancilla_qubits[0:8]   # one ancilla per edge: 1 iff edge is proper (colors differ)
    final = ancilla_qubits[8]        # AND of all edge-proper flags

    def edge_diff_compute(v, w, anc):
        # Set anc = 1 iff decoded colors of v and w differ.
        # Colors: c in {0,1,2,3} with 3->0. differ means decode(a)!=decode(b).
        # decode maps: 00->0, 01->1, 10->2, 11->0.
        # Equivalent color equality classes: {00,11}=0, {01}=1, {10}=2.
        # Two vertices same color iff:
        #   both in {00,11}, or both ==01, or both ==10.
        # We compute "same" then flip to get "diff".
        # Use compute of equality-of-color into anc via helper ancillas.
        pass

    # We compute per-edge "proper" (diff) flag using compute->store->uncompute per edge,
    # leveraging two scratch ancillas reused. But ancillas are limited (9 total; 8 used as
    # edge flags, 1 as final). So compute each edge flag reversibly directly into edge_anc
    # using only problem qubits as controls (no extra scratch), by enumerating the
    # "different color" condition as a sum of monochromatic exclusions.
    #
    # Simpler exact approach: anc_edge = OR over color k of (v is color k AND w is color k)
    # gives "same". We instead directly build "same" then flip.
    #
    # Color membership predicates on 2 qubits (b0 low, b1 high):
    #   color0: (b0,b1) in {00,11}  == (b0 == b1)
    #   color1: (b0,b1) == 01       == b0 & ~b1
    #   color2: (b0,b1) == 10       == ~b0 & b1
    #
    # same(v,w) = [c0(v)&c0(w)] | [c1(v)&c1(w)] | [c2(v)&c2(w)]
    # These three terms are mutually exclusive, so OR == XOR == sum.
    # So we can accumulate each term into the edge ancilla with mcx, then the ancilla
    # holds "same" (1 iff monochromatic). proper = NOT same, so we mark f=1 when all
    # edges proper, i.e. all edge "same" ancillas == 0.

    def add_color0_control_ pass  # placeholder removed below


    # Compute "same" flag for an edge into target ancilla a.
    def compute_same(v, w, a):
        v0, v1 = qb(v)
        w0, w1 = qb(w)
        # term c0&c0: c0 == (b0==b1) == NOT(b0 xor b1).
        # Represent b0==b1 by mapping: temporarily set v1 := v0 xor v1 (so v1==0 means equal),
        # then c0(v) == (v1_mapped == 0). Do same for w. Then term contributes when
        # v1_mapped==0 and w1_mapped==0 -> use X on those lines and a 2-control mcx.
        # But we must not disturb problem qubits permanently; we do it locally & undo.
        qc.cx(v0, v1)   # v1 <- v0 xor v1 ; now v1==0 iff original color0
        qc.cx(w0, w1)   # w1 <- w0 xor w1 ; now w1==0 iff original color0
        # term0: both color0 -> v1==0 and w1==0
        qc.x(v1); qc.x(w1)
        qc.ccx(v1, w1, a)
        qc.x(v1); qc.x(w1)
        # undo mapping to restore original problem qubits before doing color1/2 terms
        qc.cx(v0, v1)
        qc.cx(w0, w1)
        # term1: both color1 -> (v0=1,v1=0) and (w0=1,w1=0)
        qc.x(v1); qc.x(w1)
        qc.mcx([v0, v1, w0, w1], a)
        qc.x(v1); qc.x(w1)
        # term2: both color2 -> (v0=0,v1=1) and (w0=0,w1=1)
        qc.x(v0); qc.x(w0)
        qc.mcx([v0, v1, w0, w1], a)
        qc.x(v0); qc.x(w0)

    def uncompute_same(v, w, a):
        v0, v1 = qb(v)
        w0, w1 = qb(w)
        # exact reverse of compute_same
        qc.x(v0); qc.x(w0)
        qc.mcx([v0, v1, w0, w1], a)
        qc.x(v0); qc.x(w0)
        qc.x(v1); qc.x(w1)
        qc.mcx([v0, v1, w0, w1], a)
        qc.x(v1); qc.x(w1)
        qc.cx(v0, v1)
        qc.cx(w0, w1)
        qc.x(v1); qc.x(w1)
        qc.ccx(v1, w1, a)
        qc.x(v1); qc.x(w1)
        qc.cx(v0, v1)
        qc.cx(w0, w1)

    # Compute all edge "same" flags.
    for (v, w), a in zip(edges, edge_anc):
        compute_same(v, w, a)

    # f = 1 iff every edge proper == every edge "same" flag is 0.
    # Flip all edge flags, multi-control on all being 1 (i.e. all originally 0), phase.
    for a in edge_anc:
        qc.x(a)
    qc.h(final)
    qc.mcx(edge_anc, final)
    qc.h(final)
    for a in edge_anc:
        qc.x(a)

    # Uncompute all edge flags (reverse order).
    for (v, w), a in reversed(list(zip(edges, edge_anc))):
        uncompute_same(v, w, a)
