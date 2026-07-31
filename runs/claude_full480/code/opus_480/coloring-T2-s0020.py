import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (2, 3), (3, 4)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # We need to detect, for each edge (u,w), whether color(u) == color(w).
    # color(u)==color(w) means both decode to same color in {0,1,2}.
    # Decoding: c=0->0, c=1->1, c=2->2, c=3->0.
    # So color(u)==color(w) iff:
    #   (cu==cw) with cu,cw in {0,1,2}, OR combos giving color 0:
    #   color 0 codes = {00, 11}; color1 = {01}; color2 = {10}.
    # Two vertices same color iff:
    #   both in {00,11}  (color 0), OR both == 01 (color1), OR both == 10 (color2).
    #
    # Edge "different" (good) iff NOT same color.
    # f(x) = AND over edges of (different).
    #
    # For each edge, compute an ancilla bit e = 1 iff SAME color (monochromatic).
    # Then f = 1 iff all e == 0, i.e. apply phase -1 when all edge-ancillas are 0.
    #
    # We process edges one at a time into a single "any-conflict" accumulator is
    # hard to uncompute cleanly with phase; instead compute all 7 edge-conflict
    # bits into 7 ancillas, then apply phase -1 conditioned on all being 0
    # (multi-controlled with negative controls), then uncompute.
    #
    # We have 8 ancillas; use ancilla_qubits[0..6] for 7 edges, ancilla_qubits[7]
    # as scratch for computing each edge conflict.

    edge_anc = ancilla_qubits[0:7]
    scratch = ancilla_qubits[7]

    def compute_conflict(u, w, out):
        # Set out = 1 iff u and w have the same decoded color.
        u0, u1 = qb(u)
        w0, w1 = qb(w)
        # Case A: both color 0 -> u in {00,11} and w in {00,11}.
        #   u in {00,11}: u0 == u1  -> (u0 XNOR u1)
        #   w in {00,11}: w0 == w1
        # Case B: both == 01: u0=1,u1=0 and w0=1,w1=0.
        # Case C: both == 10: u0=0,u1=1 and w0=0,w1=1.
        #
        # Same color iff (colorU == colorW). Equivalent: the pair matches one case.
        #
        # Simpler exact route: same color iff for the two codes cu,cw,
        # decode equal. We build the three case-terms and OR them into out.

        # --- Case B: both codes == 01 (u0&~u1 & w0&~w1) ---
        # Use scratch pattern with X on the qubits that must be 0.
        qc.x(u1); qc.x(w1)
        qc.mcx([u0, u1, w0, w1], out)
        qc.x(u1); qc.x(w1)

        # --- Case C: both codes == 10 (~u0&u1 & ~w0&w1) ---
        qc.x(u0); qc.x(w0)
        qc.mcx([u0, u1, w0, w1], out)
        qc.x(u0); qc.x(w0)

        # --- Case A: both color 0 -> (u0==u1) AND (w0==w1) ---
        # (u0==u1): compute p = ~(u0 XOR u1) ; (w0==w1): q = ~(w0 XOR w1)
        # We need out ^= p AND q, without extra ancilla beyond available.
        # Use w1 side: compute equality flags into u0? No — must not disturb inputs
        # permanently. Instead realize p AND q via controls with X-conjugation:
        # p = 1 iff u0==u1. Encode by mapping: set u1 ^= u0 so u1 now = XOR; then
        # ~XOR means u1==0. Similarly w1 ^= w0. Then term = (u1==0)&(w1==0).
        qc.cx(u0, u1)
        qc.cx(w0, w1)
        qc.x(u1); qc.x(w1)
        qc.mcx([u1, w1], out)
        qc.x(u1); qc.x(w1)
        qc.cx(w0, w1)
        qc.cx(u0, u1)

    # Compute all edge conflicts.
    for (u, w), a in zip(edges, edge_anc):
        compute_conflict(u, w, a)

    # Phase: -1 iff every edge-conflict bit is 0 (all edges properly colored).
    for a in edge_anc:
        qc.x(a)
    # multi-controlled Z on all edge-anc (now 1 iff originally all 0), target scratch
    qc.h(scratch)
    qc.mcx(edge_anc, scratch)
    qc.h(scratch)
    for a in edge_anc:
        qc.x(a)

    # Uncompute edge conflicts (mirror).
    for (u, w), a in zip(reversed(edges), reversed(edge_anc)):
        compute_conflict(u, w, a)
