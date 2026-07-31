from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0,1),(0,2),(0,3),(0,4),(1,2),(1,3),(1,4)]

    def qb(v, bit):
        return problem_qubits[2*v + bit]

    edge_anc = ancilla_qubits[0]   # set to 1 while an edge is monochromatic
    tmp = ancilla_qubits[1]        # per-edge "same color" flag
    t0 = ancilla_qubits[2]         # helper for color-value equality checks
    t1 = ancilla_qubits[3]         # helper

    # color(v): c0 = b0 OR (b1)?  Decoding: c=0->0,1->1,2->2,3->0.
    # Two vertices share a color iff their decoded colors are equal.
    # Decoded color as a function of (b0,b1):
    #   (0,0)->0, (1,0)->1, (0,1)->2, (1,1)->0
    # Represent color by a 2-bit "canonical" pair (d0,d1):
    #   color0 -> (0,0), color1 -> (1,0), color2 -> (0,1)
    # Canonicalization: (b0,b1)=(1,1) must map to (0,0).
    #   d0 = b0 AND (NOT b1)
    #   d1 = b1 AND (NOT b0)
    # Two vertices same color iff d0_u==d0_v AND d1_u==d1_v.

    def compute_canon(v, out0, out1):
        # out0 = b0 & ~b1 ; out1 = b1 & ~b0   (assumes out0,out1 start at |0>)
        b0 = qb(v,0); b1 = qb(v,1)
        # out0 = b0 & ~b1  -> use ccx with b1 negated
        qc.x(b1)
        qc.ccx(b0, b1, out0)
        qc.x(b1)
        # out1 = b1 & ~b0
        qc.x(b0)
        qc.ccx(b1, b0, out1)
        qc.x(b0)

    def uncompute_canon(v, out0, out1):
        b0 = qb(v,0); b1 = qb(v,1)
        qc.x(b0)
        qc.ccx(b1, b0, out1)
        qc.x(b0)
        qc.x(b1)
        qc.ccx(b0, b1, out0)
        qc.x(b1)

    # For each edge, mark tmp=1 if the two endpoints have equal canonical pair.
    # We accumulate: edge_anc gets flipped once per monochromatic edge.
    # We need edge_anc == parity of (#monochromatic edges). But for the phase
    # we want -1 iff ALL edges are properly colored, i.e. NO monochromatic edge.
    # Strategy: compute a flag "any_mono" via OR is hard reversibly; instead
    # count is not what we want. Use: good iff for every edge the endpoints differ.
    #
    # We build edge_anc to hold 1 iff there EXISTS a monochromatic edge, using
    # the standard trick: set a per-edge same-flag, and OR it into edge_anc via
    # multi-controlled logic. OR reversibly: edge_anc = NOT(AND over edges of
    # (not same_e)). We compute prod of "different" flags into edge_anc meaning
    # edge_anc=1 iff all edges different (the good case), then phase on edge_anc.

    # per-edge "different" flag diff_e = NOT same_e, ANDed cumulatively into
    # edge_anc using a chain. Simpler: compute AND of all diff_e via a big MCX
    # over per-edge diff qubits — but we have limited ancillas. Instead do a
    # sequential AND using edge_anc as running product with a fresh diff each time
    # is not reversible easily. We use the running-product on edge_anc:
    #   want edge_anc final = AND_e diff_e.
    # Do it by first setting edge_anc=1 (X), then for each edge if same_e then
    # clear... clearing conditionally is not simply reversible across edges.
    #
    # Cleanest correct approach: build the product using controlled logic where
    # edge_anc = 1 initially, and we AND-in each diff_e with a Toffoli into a
    # fresh running register. With only 4 ancillas we instead compute, per edge,
    # same_e into tmp, and apply a controlled phase contribution — but phase
    # must be conditioned on ALL edges good, i.e. a single global condition.

    # Given the ancilla budget, use this exact reversible construction:
    #   good = AND over edges of diff_e.
    # We realize AND over edges by toggling edge_anc to 1 (good assumption) and
    # for EACH edge, compute same_e into tmp; every same_e that is 1 must force
    # good=0. Equivalent: good = NOT(OR same_e). Use De Morgan with edge_anc as
    # the OR accumulator (parity won't do). Reversible OR into a target:
    #   OR_target ^= same_e  is XOR, not OR. To get OR we track via: target=1
    #   iff any same_e=1. Implement by: for each edge, CX same_e->edge_anc only
    #   when edge_anc still 0. That conditioning = mcx with edge_anc negated.

    # edge_anc = OR of same_e implemented incrementally:
    #   if same_e and (edge_anc==0): set edge_anc=1
    #   -> ccx(same_e, ~edge_anc, edge_anc): but that's just when edge_anc 0,
    #      flipping to 1; when edge_anc already 1 it stays. This equals OR. Good,
    #      and it's its own inverse run in reverse order for uncompute.

    def edge_same_into_tmp(e):
        u, v = e
        compute_canon(u, t0, t1)
        # now compute canon of v into edge... need two more; reuse by comparing
        # We compare canon(u) in (t0,t1) with canon(v) computed on the fly.
        # same iff t0==b0v_canon and t1==b1v_canon.
        # Compute canon(v) into (edge_anc? no). We need two temps for v, but t0,t1
        # are used. Instead compute equality directly:
        # Build v's canon into local: we only have tmp free plus edge_anc busy.
        # Use the identity: same iff (t0 XOR d0v)==0 and (t1 XOR d1v)==0.
        # We can XOR d0v,d1v onto t0,t1 (turning them into difference bits),
        # then same iff t0==0 and t1==0, i.e. tmp ^= (NOT t0)AND(NOT t1).
        b0 = qb(v,0); b1 = qb(v,1)
        # t0 ^= d0v = b0 & ~b1
        qc.x(b1); qc.ccx(b0, b1, t0); qc.x(b1)
        # t1 ^= d1v = b1 & ~b0
        qc.x(b0); qc.ccx(b1, b0, t1); qc.x(b0)
        # now t0 = d0u XOR d0v, t1 = d1u XOR d1v; same iff both zero
        qc.x(t0); qc.x(t1)
        qc.ccx(t0, t1, tmp)   # tmp ^= 1 iff same
        qc.x(t0); qc.x(t1)
        # uncompute t0,t1 back to 0
        qc.x(b0); qc.ccx(b1, b0, t1); qc.x(b0)
        qc.x(b1); qc.ccx(b0, b1, t0); qc.x(b1)
        uncompute_canon(u, t0, t1)

    # Compute edge_anc = OR over edges of same_e
    for e in edges:
        edge_same_into_tmp(e)             # tmp = same_e (was 0)
        # edge_anc |= tmp : if tmp and edge_anc==0 -> set edge_anc
        qc.x(edge_anc)
        qc.ccx(tmp, edge_anc, edge_anc)   # note: edge_anc negated then control
        qc.x(edge_anc)
        # NOTE the above two-x wrapping makes control on edge_anc==0
        # uncompute tmp
        edge_same_into_tmp(e)             # tmp back to 0

    # Now edge_anc == 1 iff there EXISTS a monochromatic edge (bad).
    # good iff edge_anc==0. Apply phase -1 on the good states:
    qc.x(edge_anc)
    qc.z(edge_anc)
    qc.x(edge_anc)

    # Uncompute edge_anc back to 0 (mirror of the OR accumulation)
    for e in reversed(edges):
        edge_same_into_tmp(e)
        qc.x(edge_anc)
        qc.ccx(tmp, edge_anc, edge_anc)
        qc.x(edge_anc)
        edge_same_into_tmp(e)
