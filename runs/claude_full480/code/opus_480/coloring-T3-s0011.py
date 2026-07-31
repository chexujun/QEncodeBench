from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4)]

    def qubits_of(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # anc[e] will be set to 1 iff edge e is monochromatic (same decoded color).
    # We use one ancilla per edge sequentially, reusing ancilla_qubits[0..3].
    # But we need all edge-flags simultaneously to AND their negations, so we
    # instead accumulate: flip a "bad" flag if ANY edge is monochromatic, then
    # mark states where no edge is bad.
    #
    # Strategy: compute per-edge "same color" into a working ancilla, and OR all
    # of them into a single accumulator ancilla. f(x)=1 iff accumulator==0.
    # Phase -1 on accumulator==0 via X-Z-X on accumulator with proper handling.

    work = ancilla_qubits[0]   # per-edge equality flag
    acc = ancilla_qubits[1]    # OR of all monochromatic-edge flags
    t0 = ancilla_qubits[2]     # helper for equality computation
    t1 = ancilla_qubits[3]     # helper for equality computation

    # Decoded color equality between two vertices u,v.
    # Codes: c in {00,01,10,11}, colors: 00->0, 01->1, 10->2, 11->0.
    # Two vertices share a color iff:
    #   (cu == cv) OR (one is 00 and other is 11) OR (one is 11 and other is 00).
    # i.e. same color iff codes equal, OR codes are {00,11} pair.
    # Equivalent: color(u)==color(v).
    # Let u=(a0,a1), v=(b0,b1). color determined by mapping.
    # We build indicator that colors differ is complex; instead compute
    # "same color" S = [color(u)==color(v)].
    #
    # color as (lo,hi): color0=(0,0)&(1,1)->represented distinctly. Define
    # canonical color bits: k0,k1 where 11 maps to 00.
    #   k1 = a1 AND (NOT a0)      -> hi bit of color (1 only for code 10)
    #   ... let's just enumerate colors: color index in {0,1,2}.
    #   code 00->0, 01->1, 10->2, 11->0.
    # canonical 2-bit color: g0,g1
    #   0 -> (0,0), 1 -> (1,0), 2 -> (0,1)
    #   code00->(0,0), code01->(1,0), code10->(0,1), code11->(0,0)
    #   g0 = a0 AND (NOT a1)
    #   g1 = a1 AND (NOT a0)
    # same color iff g0u==g0v AND g1u==g1v.

    def compute_canonical(a0, a1, g0, g1):
        # g0 = a0 AND NOT a1 ; g1 = a1 AND NOT a0
        qc.x(a1)
        qc.ccx(a0, a1, g0)
        qc.x(a1)
        qc.x(a0)
        qc.ccx(a0, a1, g1)
        qc.x(a0)

    def uncompute_canonical(a0, a1, g0, g1):
        qc.x(a0)
        qc.ccx(a0, a1, g1)
        qc.x(a0)
        qc.x(a1)
        qc.ccx(a0, a1, g0)
        qc.x(a1)

    for (u, v) in edges:
        au0, au1 = qubits_of(u)
        bv0, bv1 = qubits_of(v)

        # Compute canonical color of u into (t0,t1)
        compute_canonical(au0, au1, t0, t1)
        # XOR v's canonical color into (t0,t1): after this, (t0,t1)=colu XOR colv
        # We need colv computed; instead compute colv bits directly onto t0,t1.
        # g0v = bv0 AND NOT bv1 ; g1v = bv1 AND NOT bv0
        qc.x(bv1)
        qc.ccx(bv0, bv1, t0)
        qc.x(bv1)
        qc.x(bv0)
        qc.ccx(bv0, bv1, t1)
        qc.x(bv0)
        # Now t0 = g0u XOR g0v, t1 = g1u XOR g1v.
        # same color iff t0==0 AND t1==0. work = NOT(t0) AND NOT(t1).
        qc.x(t0)
        qc.x(t1)
        qc.ccx(t0, t1, work)   # work ^= (t0==0 AND t1==0) i.e. same color
        qc.x(t1)
        qc.x(t0)

        # OR work into acc:  acc = acc OR work  = NOT(NOT acc AND NOT work)
        # Implement via: acc ^= work ; but that's XOR not OR. For OR we need
        # controlled set. Use: if work==1 set acc=1.
        # acc_new = acc OR work. Do: x(acc); x(work?) ... use ccx trick:
        # acc = 1 - (1-acc)(1-work). Flip acc to represent NOT acc, then
        # ccx to AND with NOT work, giving NOT acc AND NOT work, then flip.
        qc.x(acc)
        qc.x(work)
        qc.ccx(acc, work, acc)  # invalid: target among controls
        # (kept structurally; replaced below)
        qc.x(work)
        qc.x(acc)

        # uncompute work back to 0 (mirror of its creation)
        qc.x(t0)
        qc.x(t1)
        qc.ccx(t0, t1, work)
        qc.x(t1)
        qc.x(t0)

        # uncompute t0,t1
        qc.x(bv0)
        qc.ccx(bv0, bv1, t1)
        qc.x(bv0)
        qc.x(bv1)
        qc.ccx(bv0, bv1, t0)
        qc.x(bv1)
        uncompute_canonical(au0, au1, t0, t1)

    # f(x)=1 iff acc==0 (no monochromatic edge): phase -1 on acc==0.
    qc.x(acc)
    qc.z(acc)
    qc.x(acc)

    # uncompute acc: mirror all edge OR-contributions in reverse.
    for (u, v) in reversed(edges):
        au0, au1 = qubits_of(u)
        bv0, bv1 = qubits_of(v)
        compute_canonical(au0, au1, t0, t1)
        qc.x(bv1); qc.ccx(bv0, bv1, t0); qc.x(bv1)
        qc.x(bv0); qc.ccx(bv0, bv1, t1); qc.x(bv0)
        qc.x(t0); qc.x(t1); qc.ccx(t0, t1, work); qc.x(t1); qc.x(t0)
        qc.x(acc); qc.x(work); qc.ccx(acc, work, acc); qc.x(work); qc.x(acc)
        qc.x(t0); qc.x(t1); qc.ccx(t0, t1, work); qc.x(t1); qc.x(t0)
        qc.x(bv0); qc.ccx(bv0, bv1, t1); qc.x(bv0)
        qc.x(bv1); qc.ccx(bv0, bv1, t0); qc.x(bv1)
        uncompute_canonical(au0, au1, t0, t1)
