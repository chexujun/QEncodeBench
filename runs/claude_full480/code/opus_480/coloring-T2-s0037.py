from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits) -> None:
    edges = [(0,1),(0,2),(1,2),(1,3),(1,4),(2,3),(3,4)]

    def qbits(v):
        return problem_qubits[2*v], problem_qubits[2*v+1]

    # For each edge we compute a "same-color" flag into a per-edge ancilla.
    # Two vertices u,v have the same color iff decode(cu)==decode(cv).
    # Codes: 00->0, 01->1, 10->2, 11->0. So color equality:
    #   same iff (cu==cv) OR (one is 00 and other is 11) OR (one is 11 and other is 00).
    # Equivalently decode maps c to color; color(c)=0 for c in {00,11}, 1 for 01, 2 for 10.
    # same-color(u,v) = (color_u == color_v).
    #
    # Let u bits (a0,a1), v bits (b0,b1).
    # color0 (=0): (a0,a1) in {(0,0),(1,1)}  i.e. a0==a1
    # color1 (=1): (a0,a1)=(1,0)  -> a0=1,a1=0
    # color2 (=2): (a0,a1)=(0,1)  -> a0=0,a1=1
    #
    # same-color iff:
    #   both color0: (a0==a1) AND (b0==b1)
    #   both color1: a0 & ~a1 & b0 & ~b1
    #   both color2: ~a0 & a1 & ~b0 & b1
    #
    # We compute per-edge flag = OR of these three mutually exclusive terms.
    # f(x)=1 iff NO edge is same-color, i.e. AND over edges of (NOT same-color).
    #
    # Strategy: compute each edge same-flag into edge ancilla; then f=1 iff all
    # edge ancillas are 0. Apply phase -1 when all edge ancillas==0 using an
    # X-wrapped multi-controlled Z. Then uncompute.
    #
    # We have 8 ancillas, 7 edges. Use ancilla[i] for edge i (7 ancillas),
    # and ancilla[7] as scratch for term computation.

    edge_anc = ancilla_qubits[:7]
    scratch = ancilla_qubits[7]

    def compute_same(u, v, flag):
        a0, a1 = qbits(u)
        b0, b1 = qbits(v)
        # term both color1: a0 & ~a1 & b0 & ~b1  -> flag ^= that
        qc.x(a1); qc.x(b1)
        qc.mcx([a0, a1, b0, b1], flag)
        qc.x(a1); qc.x(b1)
        # term both color2: ~a0 & a1 & ~b0 & b1
        qc.x(a0); qc.x(b0)
        qc.mcx([a0, a1, b0, b1], flag)
        qc.x(a0); qc.x(b0)
        # term both color0: (a0==a1) & (b0==b1)
        # a0==a1 : compute into scratch = a0 xor a1 xor 1
        qc.cx(a0, scratch); qc.cx(a1, scratch); qc.x(scratch)
        # now scratch = (a0==a1). Need also (b0==b1). Use another temp? only one scratch.
        # Combine: flag ^= scratch & (b0==b1).
        # (b0==b1) = b0 xor b1 xor 1. Build a controlled condition without extra ancilla:
        # We fold b0,b1 into scratch too? That would destroy scratch meaning.
        # Instead: temporarily make scratch = (a0==a1) AND (b0==b1) using reversible trick:
        # scratch currently (a0==a1). XOR into flag conditioned on scratch & (b0==b1)==1.
        # Use mcx with controls scratch, and (b0==b1) expressed by x-wrapping b0,b1 and
        # requiring b0==b1... but mcx needs both b0,b1 equal which isn't a single control.
        # b0==b1 true in two cases (00,11); not a product term. So compute (b0 xor b1) into
        # a second folding on scratch: set scratch2.
        # We only have one scratch. Do it in two sub-steps reusing flag path:
        # Uncompute scratch back first:
        qc.x(scratch); qc.cx(a1, scratch); qc.cx(a0, scratch)  # scratch back to |0>
        # Product-term approach for color0 equality:
        # both color0 <=> a0==a1 AND b0==b1. Enumerate 2 x-patterns each -> 4 product terms:
        #  (a0=0,a1=0,b0=0,b1=0), (0,0,1,1),(1,1,0,0),(1,1,1,1)
        for pa in [(0,0),(1,1)]:
            for pb in [(0,0),(1,1)]:
                flips = []
                if pa[0]==0: flips.append(a0)
                if pa[1]==0: flips.append(a1)
                if pb[0]==0: flips.append(b0)
                if pb[1]==0: flips.append(b1)
                for q in flips: qc.x(q)
                qc.mcx([a0, a1, b0, b1], flag)
                for q in flips: qc.x(q)

    # compute all edge flags
    for i, (u, v) in enumerate(edges):
        compute_same(u, v, edge_anc[i])

    # phase -1 iff all edge flags are 0: X all, multi-controlled Z, X all
    for q in edge_anc:
        qc.x(q)
    qc.h(edge_anc[-1])
    qc.mcx(edge_anc[:-1], edge_anc[-1])
    qc.h(edge_anc[-1])
    for q in edge_anc:
        qc.x(q)

    # uncompute edge flags (mirror)
    for i in reversed(range(len(edges))):
        u, v = edges[i]
        compute_same(u, v, edge_anc[i])
