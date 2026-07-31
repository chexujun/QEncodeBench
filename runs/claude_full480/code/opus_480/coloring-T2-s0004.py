import numpy as np
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 2), (1, 2), (1, 3), (1, 4), (3, 4)]

    def vq(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # For an edge (u,w): vertices share a color iff their decoded colors are equal.
    # Decode: c=0/3 -> color0, c=1 -> color1, c=2 -> color2.
    # color0(v)  = (b0==0 & b1==0) | (b0==1 & b1==1)  = (b0 XNOR b1)
    # color1(v)  = (b0==1 & b1==0)
    # color2(v)  = (b0==0 & b1==1)
    # Edge is "same color" iff both are color0, or both color1, or both color2.
    #
    # Strategy: for each edge, compute a "same" flag into a scratch ancilla,
    # OR-accumulate that any edge is same into a "violation" register via a
    # multi-controlled scheme. Simpler: compute per-edge "different" flag and
    # AND all of them together; f = AND of all edges different.
    #
    # We compute for each edge an ancilla d_e = 1 iff colors differ, then
    # multi-control on all d_e = 1 to apply phase, then uncompute.

    n_edges = len(edges)
    edge_anc = ancilla_qubits[:n_edges]        # one per edge (5)
    scratch = ancilla_qubits[n_edges]          # 1 scratch (index 5)

    # Helper: for vertex v put color0/1/2 predicate onto scratch temporarily.
    # We instead directly build "same color" for an edge using scratch, writing
    # into edge_anc as "different" = NOT same.

    def edge_compute(u, w, dest, undo=False):
        u0, u1 = vq(u)
        w0, w1 = vq(w)
        # same_color0: color0(u) & color0(w); color0 = b0 XNOR b1.
        # Compute color0(u) into scratch via: set scratch=1 then it equals XNOR.
        # XNOR(b0,b1): scratch = 1 ^ b0 ^ b1.
        # both color0 -> need color0(u)&color0(w). We use scratch for color0(u),
        # and toggle dest when color0(u)=1 and color0(w)=1.
        ops = []

        # --- same via color0: dest ^= color0(u) & color0(w) ---
        # color0(u) into scratch
        ops.append(('x', scratch))
        ops.append(('cx', u0, scratch))
        ops.append(('cx', u1, scratch))
        # now scratch = 1^u0^u1 = XNOR(u0,u1) = color0(u)
        # need color0(w) = 1^w0^w1 as a control too; build via temporary toggles
        # dest ^= scratch & color0(w). color0(w)=1^w0^w1. Use mcx with controls
        # scratch and a second scratch? We only have one scratch. So decompose:
        # dest ^= scratch & (1^w0^w1)
        #   = scratch ^ scratch&w0 ^ scratch&w1   (mod 2)
        ops.append(('ccx_pos', scratch, None, dest, 'const'))  # placeholder
        return ops

    # The above got unwieldy; implement directly below without helper.

    # Clear placeholder approach; do explicit gate emission per edge.
    def apply_edge(u, w, dest):
        u0, u1 = vq(u)
        w0, w1 = vq(w)
        s = scratch
        # dest ^= same(u,w) where
        # same = color0(u)&color0(w) + color1(u)&color1(w) + color2(u)&color2(w)
        # (these three terms are mutually exclusive, so + == XOR)
        #
        # ---- term color1: color1=b0 & ~b1 ; both -> u0 & ~u1 & w0 & ~w1 ----
        qc.x(u1); qc.x(w1)
        qc.mcx([u0, u1, w0, w1], dest)
        qc.x(u1); qc.x(w1)
        # ---- term color2: color2=~b0 & b1 ; both -> ~u0 & u1 & ~w0 & w1 ----
        qc.x(u0); qc.x(w0)
        qc.mcx([u0, u1, w0, w1], dest)
        qc.x(u0); qc.x(w0)
        # ---- term color0: color0 = XNOR(b0,b1). both color0 ----
        # color0(u) into s:
        qc.x(s); qc.cx(u0, s); qc.cx(u1, s)   # s = color0(u)
        # color0(w) into u-independent temp: we need a second flag. Reuse dest?
        # Instead expand: dest ^= s & color0(w), color0(w)=1^w0^w1
        #   dest ^= s ; dest ^= s&w0 ; dest ^= s&w1
        qc.cx(s, dest)
        qc.ccx(s, w0, dest)
        qc.ccx(s, w1, dest)
        # uncompute s
        qc.cx(u1, s); qc.cx(u0, s); qc.x(s)

    # Compute "same" flags for every edge into edge_anc.
    for e, (u, w) in enumerate(edges):
        apply_edge(u, w, edge_anc[e])

    # Now edge_anc[e] = 1 iff edge e is monochromatic.
    # f(x) = 1 iff ALL edges differ iff ALL edge_anc == 0.
    # Apply phase -1 when all edge_anc == 0: X all, multi-controlled Z, X all.
    for e in range(n_edges):
        qc.x(edge_anc[e])
    # multi-controlled Z on edge_anc: use mcp(pi)
    qc.h(edge_anc[-1])
    qc.mcx(edge_anc[:-1], edge_anc[-1])
    qc.h(edge_anc[-1])
    for e in range(n_edges):
        qc.x(edge_anc[e])

    # Uncompute the "same" flags (mirror).
    for e, (u, w) in reversed(list(enumerate(edges))):
        apply_edge(u, w, edge_anc[e])
