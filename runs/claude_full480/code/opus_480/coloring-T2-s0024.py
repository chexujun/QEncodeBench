import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (2, 3), (2, 4)]

    def qb(v, bit):
        return problem_qubits[2 * v + bit]

    # ancilla layout: for each edge use one ancilla to hold "same color" flag.
    # But we have 7 edges and only 8 ancillas; we can reuse an edge ancilla
    # sequentially and accumulate into a final AND. Instead: compute each edge's
    # "different" flag into edge_anc, AND all into a result ancilla, phase, uncompute.
    #
    # Colors: c in {0,1,2,3} with 3 -> 0. So color(v)=0 iff code==00 or code==11,
    # color 1 iff 01, color 2 iff 10.
    # Two vertices same color iff:
    #   both color0: (a is 00 or 11) and (b is 00 or 11)
    #   both color1: a==01 and b==01
    #   both color2: a==10 and b==10
    #
    # For an edge, "same color" is a predicate on 4 bits. We compute per edge a
    # flag = 1 iff DIFFERENT, store into edge ancilla, then require all edge flags
    # = 1 via a multi-controlled phase.

    edge_anc = ancilla_qubits[0]      # scratch per edge
    color_anc = ancilla_qubits[1:4]   # 3 ancillas: color0/1/2 match flags
    result = ancilla_qubits[4]        # per-edge "same" flag accumulator location

    # We'll build a list of "different" flag qubits, one per edge, then MCX phase.
    # But only limited ancillas. Use approach: compute each edge same-flag into a
    # dedicated qubit among ancillas[4..], but 7 edges need 7 qubits + scratch.
    #
    # Available ancillas indices 0..7 (8 total). Use ancilla 7 as scratch, and
    # ancillas 0..6 (7 qubits) as per-edge SAME flags.
    same = ancilla_qubits[0:7]        # 7 per-edge same-color flags
    scr = ancilla_qubits[7]           # scratch

    def color_match_terms(v, out_qubits):
        # returns nothing; caller manages. We define helper below inline.
        pass

    def set_same(edge_idx, u, v):
        # out = same[edge_idx], scratch = scr
        out = same[edge_idx]
        u0, u1 = qb(u, 0), qb(u, 1)
        v0, v1 = qb(v, 0), qb(v, 1)

        # Term A: both color 1  -> u==01 and v==01: u0=1,u1=0,v0=1,v1=0
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], out)
        qc.x(u1); qc.x(v1)

        # Term B: both color 2 -> u==10 and v==10: u0=0,u1=1,v0=0,v1=1
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], out)
        qc.x(u0); qc.x(v0)

        # Term C: both color 0 -> u in {00,11} and v in {00,11}
        # u color0 iff (u0 == u1). Compute cu = NOT(u0 xor u1) into scr region?
        # We need two scratch bits but only one scr. Compute u-color0 into scr,
        # v-color0 must go somewhere: reuse out is target. Use a nested approach:
        # cu = (u0==u1): scr = u0 xor u1 then flip -> 1 iff equal
        qc.cx(u0, scr); qc.cx(u1, scr); qc.x(scr)   # scr = (u0==u1)
        # cv = (v0==v1): need another bit; encode into out via controlled logic:
        # We want out ^= scr AND cv. Compute cv on the fly using v0,v1 with scr as
        # one control isn't enough. Use temporary: put cv into out? out is target.
        # Instead compute AND(scr, (v0==v1)) using an mcx with a second scratch.
        # We reuse: temporarily build cv on 'out' is bad. So do it via two mcx that
        # cancel the (v0==v1) construction on scr? Not enough qubits.
        #
        # Alternative: (v0==v1) == NOT(v0 xor v1). Enumerate the two v-values:
        #   v==00: v0=0,v1=0 ; v==11: v0=1,v1=1
        # So out ^= scr AND [ (v0=0,v1=0) OR (v0=1,v1=1) ]
        # Do two controlled terms:
        qc.x(v0); qc.x(v1)
        qc.mcx([scr, v0, v1], out)   # v==00 branch
        qc.x(v0); qc.x(v1)
        qc.mcx([scr, v0, v1], out)   # v==11 branch
        # uncompute scr
        qc.x(scr); qc.cx(u1, scr); qc.cx(u0, scr)   # scr back to 0

    # compute all edge same-flags
    for idx, (u, v) in enumerate(edges):
        set_same(idx, u, v)

    # f(x)=1 iff every edge is DIFFERENT, i.e. all same-flags == 0.
    # Apply phase -1 iff all same[i]==0: flip all, multi-controlled Z, flip back.
    for q in same:
        qc.x(q)
    qc.h(same[-1])
    qc.mcx(same[:-1], same[-1])
    qc.h(same[-1])
    for q in same:
        qc.x(q)

    # uncompute all edge same-flags (mirror, reverse order)
    for idx in reversed(range(len(edges))):
        u, v = edges[idx]
        set_same(idx, u, v)
