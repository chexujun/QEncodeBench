import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 1), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_anc = ancilla_qubits[0]
    flag = ancilla_qubits[1]
    work = ancilla_qubits[2:]

    n_edges = len(edges)

    def edge_same(v, u, out):
        # Compute out ^= 1 iff color(v) == color(u), leaving scratch clean.
        # color(v): c in {0,1,2,3}, 3 -> 0. So effective color equals
        # (c==3 ? 0 : c). Equivalent: two vertices share a color iff
        # decode(cv) == decode(uv).
        v0, v1 = qb(v)
        u0, u1 = qb(u)
        # temp registers
        dv = work[0]   # "vertex v is color-nonzero-as-1or2" helpers not enough;
        du = work[1]
        # We instead directly test equality of decoded colors using the fact
        # decoded color d(c): d0 = c0 AND (NOT c1) ... let's derive bits.
        # c=00->0(00), 01->1(01), 10->2(10), 11->0(00).
        # decoded low bit L = c0 AND NOT c1 ; decoded high bit H = c1 AND NOT c0.
        # Compute Lv,Hv into dv,du? need 4 scratch bits.
        Lv, Hv, Lu, Hu = work[0], work[1], work[2], work[3]
        eqL, eqH = work[4], work[5]

        # Lv = v0 & ~v1
        qc.x(v1); qc.ccx(v0, v1, Lv); qc.x(v1)
        # Hv = v1 & ~v0
        qc.x(v0); qc.ccx(v1, v0, Hv); qc.x(v0)
        # Lu = u0 & ~u1
        qc.x(u1); qc.ccx(u0, u1, Lu); qc.x(u1)
        # Hu = u1 & ~u0
        qc.x(u0); qc.ccx(u1, u0, Hu); qc.x(u0)

        # eqL = NOT(Lv XOR Lu)
        qc.cx(Lv, eqL); qc.cx(Lu, eqL); qc.x(eqL)
        # eqH = NOT(Hv XOR Hu)
        qc.cx(Hv, eqH); qc.cx(Hu, eqH); qc.x(eqH)

        # colors equal iff eqL AND eqH
        qc.ccx(eqL, eqH, out)

        # uncompute scratch (mirror)
        qc.x(eqH); qc.cx(Hu, eqH); qc.cx(Hv, eqH)
        qc.x(eqL); qc.cx(Lu, eqL); qc.cx(Lv, eqL)
        qc.x(u0); qc.ccx(u1, u0, Hu); qc.x(u0)
        qc.x(u1); qc.ccx(u0, u1, Lu); qc.x(u1)
        qc.x(v0); qc.ccx(v1, v0, Hv); qc.x(v0)
        qc.x(v1); qc.ccx(v0, v1, Lv); qc.x(v1)

    # Compute "same-color" indicator per edge into a counter of violations.
    # We want f=1 iff NO edge is monochromatic, i.e. all edge_same == 0.
    # Compute each edge_same into a distinct flag qubit, then multi-control
    # on all being 0.
    same_flags = ancilla_qubits[:0]  # placeholder

    # Use flag qubit accumulation: set edge_anc for each edge, mark, unmark.
    # Strategy: compute all-edges-different predicate.
    # We'll store per-edge equality into edge_anc one at a time is not enough
    # for the AND; instead OR all equalities into edge_anc, then phase when
    # edge_anc == 0.
    #
    # OR of equalities: edge_anc = 1 iff any edge monochromatic.
    # Computing OR incrementally requires the sub-terms; we can OR by
    # edge_anc ^= edge_same only if terms are disjoint, which they are not.
    # So instead build OR via: edge_anc starts 0; for each edge compute
    # same into a fresh temp t, then edge_anc = edge_anc OR t. But we only
    # have limited ancillas. Do OR sequentially reusing one temp:
    #   t = edge_same(e)            (t is 0/1)
    #   edge_anc = edge_anc OR t  = NOT(NOT edge_anc AND NOT t)
    # implement OR: qc.x(edge_anc); qc.x(t); qc.ccx? need target. Use:
    #   new = a OR b into edge_anc using: edge_anc |= t
    # OR into existing bit b with new bit t: b = b OR t
    #   = b XOR (t AND NOT b)
    # ccx(t, ~b -> ) tricky. Simpler: b = NOT( NOT b AND NOT t ):
    #   x(b); x(t); ccx not available in-place. We use a helper: since we
    #   uncompute t right after, do:
    #     x(b)                      # b := ~b (so b holds ~OR-so-far)
    #     controlled: if t==1 -> set b to 0 meaning OR true.
    # Maintain invariant: edge_anc holds NOT(OR so far). Start edge_anc=1.
    qc.x(edge_anc)  # edge_anc = 1 = NOT(false)

    temp = ancilla_qubits[2]  # single temp for current edge equality
    # ensure temp not colliding with work used inside edge_same (work=anc[2:])
    # Reassign: use work starting at index 3 to leave temp at index2.
    def edge_same2(v, u, out):
        v0, v1 = qb(v); u0, u1 = qb(u)
        Lv, Hv, Lu, Hu = ancilla_qubits[3], ancilla_qubits[4], ancilla_qubits[3], ancilla_qubits[4]
        # not enough ancillas -> fall back handled below
        pass

    # We actually have 5 ancillas total: indices 0..4.
    # edge_anc = 0, temp = 2, and edge_same needs 6 scratch bits -> too many.
    # Rework equality with fewer scratch bits (2) below.

    def eq_same(v, u, out, s0, s1):
        # out ^= (decoded color v == decoded color u), using scratch s0,s1.
        v0, v1 = qb(v); u0, u1 = qb(u)
        # d0 = v0 & ~v1 ; compute into s0
        qc.x(v1); qc.ccx(v0, v1, s0); qc.x(v1)      # s0 = Lv
        qc.x(u1); qc.ccx(u0, u1, s0); qc.x(u1)      # s0 ^= Lu -> s0 = Lv XOR Lu
        # s1 = Hv XOR Hu
        qc.x(v0); qc.ccx(v1, v0, s1); qc.x(v0)      # s1 = Hv
        qc.x(u0); qc.ccx(u1, u0, s1); qc.x(u0)      # s1 ^= Hu
        # equal iff s0==0 AND s1==0
        qc.x(s0); qc.x(s1)
        qc.ccx(s0, s1, out)
        qc.x(s1); qc.x(s0)
        # uncompute s1, s0
        qc.x(u0); qc.ccx(u1, u0, s1); qc.x(u0)
        qc.x(v0); qc.ccx(v1, v0, s1); qc.x(v0)
        qc.x(u1); qc.ccx(u0, u1, s0); qc.x(u1)
        qc.x(v1); qc.ccx(v0, v1, s0); qc.x(v1)

    s0, s1 = ancilla_qubits[3], ancilla_qubits[4]

    # Build OR invariant: edge_anc holds NOT(OR of same so far), start = 1.
    for (v, u) in edges:
        # temp = same(v,u)
        eq_same(v, u, temp, s0, s1)
        # edge_anc := edge_anc AND NOT temp  (keeps NOT-OR invariant)
        qc.x(temp)
        qc.ccx(edge_anc if False else temp, temp, temp) if False else None
        # AND into edge_anc: edge_anc = edge_anc AND (NOT temp)
        # temp currently = NOT same. We need edge_anc &= temp.
        # Use: new_edge_anc = edge_anc AND temp -> implement via setting a
        # fresh bit then swapping is costly; instead use flag qubit chain.
        qc.x(temp)  # restore temp = same
        # cleanup: recompute-free AND handled with controlled below
        # Accumulate directly: if same==1 then OR true -> edge_anc(NOT-OR)=0
        # i.e. edge_anc &= NOT same:  cx-controlled reset
        qc.cx(temp, flag)  # move same into flag OR accumulator (flag=OR, disjoint? no)
        # undo temp
        eq_same(v, u, temp, s0, s1)
