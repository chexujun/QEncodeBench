from qiskit import QuantumCircuit
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 2), (0, 3), (0, 4), (1, 2), (1, 4), (3, 4)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_anc = ancilla_qubits[0:6]
    final = ancilla_qubits[6]

    def compute_edge_ok(u, v, out):
        # colors differ. color(c=3)==color(c=0). Decoded color map:
        # c=0(00)->0, c=1(01)->1, c=2(10)->2, c=3(11)->0
        # Two vertices SAME color iff:
        #   both decode to 0: u in {00,11} AND v in {00,11}
        #   both == 1: u==01 AND v==01
        #   both == 2: u==10 AND v==10
        # out should be set to 1 iff colors DIFFER (edge ok).
        # We compute SAME into out then flip.
        u0, u1 = qb(u)
        v0, v1 = qb(v)
        # We need scratch. Use two temp qubits: but budget tight.
        # Instead compute SAME directly into out via multiple mcx terms, then x(out).
        # term A: both color 0: u decodes 0 iff (u0==u1) i.e. u0 XOR u1 ==0.
        #   Represent "u is color0" = NOT(u0 XOR u1). Same for v.
        #   both0 = uc0 AND vc0.
        # We build predicate on the fly using controls with X-conditioning.
        #
        # Strategy: out = SAME. SAME is OR of three disjoint AND-terms.
        # Because color partitions are disjoint, at most one term true, so OR = XOR = sum of CCX-like.
        #
        # Term color1: u==01 (u0=1,u1=0) and v==01.
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], out)
        qc.x(u1); qc.x(v1)
        # Term color2: u==10 (u0=0,u1=1) and v==10.
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], out)
        qc.x(u0); qc.x(v0)
        # Term color0: u in {00,11} and v in {00,11}.
        # uc0 = NOT(u0 XOR u1). Compute parity into u1? We must not disturb.
        # Enumerate the 4 combos of (u code0-state, v code0-state):
        # u=00 & v=00
        qc.x(u0); qc.x(u1); qc.x(v0); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], out)
        qc.x(u0); qc.x(u1); qc.x(v0); qc.x(v1)
        # u=00 & v=11
        qc.x(u0); qc.x(u1)
        qc.mcx([u0, u1, v0, v1], out)
        qc.x(u0); qc.x(u1)
        # u=11 & v=00
        qc.x(v0); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], out)
        qc.x(v0); qc.x(v1)
        # u=11 & v=11
        qc.mcx([u0, u1, v0, v1], out)
        # now out = SAME (1 if monochromatic). Flip so out = edge_ok (1 if differ).
        qc.x(out)

    def uncompute_edge_ok(u, v, out):
        u0, u1 = qb(u)
        v0, v1 = qb(v)
        qc.x(out)
        qc.mcx([u0, u1, v0, v1], out)
        qc.x(v0); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], out)
        qc.x(v0); qc.x(v1)
        qc.x(u0); qc.x(u1)
        qc.mcx([u0, u1, v0, v1], out)
        qc.x(u0); qc.x(u1)
        qc.x(u0); qc.x(u1); qc.x(v0); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], out)
        qc.x(u0); qc.x(u1); qc.x(v0); qc.x(v1)
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], out)
        qc.x(u0); qc.x(v0)
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], out)
        qc.x(u1); qc.x(v1)

    # compute each edge_ok flag
    for i, (u, v) in enumerate(edges):
        compute_edge_ok(u, v, edge_anc[i])
    # all edges ok -> mark. AND of 6 flags into phase.
    qc.h(final)
    qc.mcx(edge_anc, final)
    qc.h(final)
    # uncompute flags
    for i, (u, v) in reversed(list(enumerate(edges))):
        uncompute_edge_ok(u, v, edge_anc[i])
