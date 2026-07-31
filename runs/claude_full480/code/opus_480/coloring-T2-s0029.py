from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0,1),(0,2),(0,3),(0,4),(1,2),(2,3),(2,4)]

    def vq(v):
        return problem_qubits[2*v], problem_qubits[2*v+1]

    # For each edge, compute an "same-color" flag into an edge ancilla.
    # Decoding: color(c) with c in {0,1,2,3} -> {0,1,2,0}. So color depends
    # on code except codes 00 and 11 both map to color 0.
    # Two vertices share color iff (colorA == colorB).
    # Represent each vertex color as one-hot over {c0,c1,c2} where:
    #   is0 = (b1==b0)   (codes 00 or 11)
    #   is1 = (b0==1 and b1==0)  -> b0 & ~b1
    #   is2 = (b1==1 and b0==0)  -> b1 & ~b0
    # Same color iff (is0_u & is0_v) | (is1_u & is1_v) | (is2_u & is2_v).
    #
    # We want f=1 iff NO edge monochromatic. Equivalent: product over edges of
    # (edge properly colored). We phase -1 on f=1.
    #
    # Strategy: compute per-edge "bad" flag (mono) into an ancilla, OR-reduce:
    # any_bad = OR of edge_bad. f = NOT any_bad. Phase -1 when any_bad==0.
    #
    # We use ancilla_qubits: [0]=edge scratch a, [1]=edge scratch b,
    # accumulate "good" count via controlled logic is complex; instead compute
    # each edge_good into a dedicated? only 8 ancillas, 7 edges. Use 7 ancillas
    # as per-edge "bad" flags, then a final multi-controlled phase on all-zero.

    ea = ancilla_qubits[0:7]   # per-edge bad flags
    s0 = ancilla_qubits[7]     # scratch for pair-match terms

    def edge_bad_compute(u, v, target):
        # target ^= same_color(u,v)
        ub0, ub1 = vq(u)
        vb0, vb1 = vq(v)
        # term is0_u & is0_v : is0 = (b0==b1). Use scratch s0.
        # is0_u: set s0 = 1 iff ub0==ub1  => s0 = NOT(ub0 xor ub1)
        # Compute match for is0: need is0_u AND is0_v.
        # We'll build each product onto target via ccx with temporary computes.

        # --- term0: is0_u & is0_v ---
        # compute is0_u into s0
        qc.cx(ub0, s0); qc.cx(ub1, s0); qc.x(s0)   # s0 = NOT(ub0 xor ub1) = is0_u
        # compute is0_v into a second temp: reuse target trick not possible.
        # We need AND of is0_u and is0_v. Compute is0_v transiently using
        # ub? no—use the two v qubits with an mcx gated by s0.
        # is0_v = NOT(vb0 xor vb1). We want target ^= s0 & is0_v.
        # Rewrite: target ^= s0 & NOT(vb0 xor vb1).
        # Let w = vb0 xor vb1 (compute into... we can toggle target twice):
        # target ^= s0 & (1 xor w) = (s0) xor (s0 & w)... need care. Use temp on vb?
        # Simplest: compute is0_v into a fresh scratch. We only have s0 free plus
        # target. Borrow: use one edge ancilla not yet used? Instead reorganize:
        # compute is0_v by flipping vb0 with vb1 then x -> but that mutates code.
        # We instead uncompute after. Toggle vb0 ^= vb1, x(vb0): vb0 becomes is0_v.
        qc.cx(vb1, vb0); qc.x(vb0)                  # vb0temp = is0_v
        qc.ccx(s0, vb0, target)                     # target ^= is0_u & is0_v
        qc.x(vb0); qc.cx(vb1, vb0)                  # restore vb0
        qc.x(s0); qc.cx(ub1, s0); qc.cx(ub0, s0)   # restore s0 -> 0

        # --- term1: is1_u & is1_v ; is1 = b0 & ~b1 ---
        qc.x(ub1); qc.x(vb1)
        # is1_u = ub0 & ~ub1 ; with ub1 flipped, ~ub1 is now ub1'. Need ub0&ub1'&vb0&vb1'
        # 4-controlled toggle of target:
        qc.mcx([ub0, ub1, vb0, vb1], target)
        qc.x(ub1); qc.x(vb1)

        # --- term2: is2_u & is2_v ; is2 = b1 & ~b0 ---
        qc.x(ub0); qc.x(vb0)
        qc.mcx([ub0, ub1, vb0, vb1], target)
        qc.x(ub0); qc.x(vb0)

    # compute all edge bad flags
    for i,(u,v) in enumerate(edges):
        edge_bad_compute(u, v, ea[i])

    # f = 1 iff all edge flags are 0. Phase -1 on that state.
    # multi-controlled Z on all ea==0: X-sandwich then mcp(pi).
    for q in ea:
        qc.x(q)
    qc.h(ea[-1])
    qc.mcx(ea[:-1], ea[-1])
    qc.h(ea[-1])
    for q in ea:
        qc.x(q)

    # uncompute edge flags (mirror)
    for i,(u,v) in reversed(list(enumerate(edges))):
        edge_bad_compute(u, v, ea[i])
