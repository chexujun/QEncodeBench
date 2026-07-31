from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 2), (0, 3), (1, 2), (1, 3), (2, 4), (3, 4)]

    def qb(v, bit):
        return problem_qubits[2 * v + bit]

    # ancillas: 6 edge-ok flags + 1 final phase ancilla
    edge_anc = ancilla_qubits[0:6]
    final_anc = ancilla_qubits[6]

    def compute_edge_ok(u, v, anc):
        # Two vertices decode to the SAME color iff:
        #   codes equal (00==00,01==01,10==10,11==11)  OR  {00,11} pair OR {11,00}
        # Concretely same color when:
        #   (cu==cv) or (cu in {00,11} and cv in {00,11})
        # We want anc = 1 iff colors DIFFER (edge ok).
        # Enumerate the "same color" set S over (cu,cv):
        #   color0 codes = {00, 11}; color1 = {01}; color2 = {10}
        # same iff both in {00,11}, or both ==01, or both ==10.
        u0, u1 = qb(u, 0), qb(u, 1)
        v0, v1 = qb(v, 0), qb(v, 1)
        # Build "same" onto anc by marking each same-pattern, then flip to get "differ".
        # anc starts |0>. We'll set anc=1 for each (cu,cv) in SAME set, then X to invert -> differ.
        # SAME patterns (u1u0, v1v0):
        #  color0 x color0: u in {00,11}, v in {00,11} -> 4 combos: (00,00),(00,11),(11,00),(11,11)
        #  (01,01), (10,10)
        # Detect "u in {00,11}" == (u0 == u1). Detect "v in {00,11}" == (v0 == v1).
        # color0 both: (u0==u1) AND (v0==v1).
        # (01,01): u0=1,u1=0,v0=1,v1=0
        # (10,10): u0=0,u1=1,v0=0,v1=1

        # Helper temp qubits: reuse anc region? We only have this anc. Use gates directly onto anc
        # via multi-controlled toggles, each condition disjoint so XORs accumulate correctly.

        # Term A: (u0==u1) AND (v0==v1)  -> use eq flags built on the fly.
        # We need scratch. Since disjoint SAME-set terms, we can toggle anc once per satisfied term;
        # but multi-controlled with equality needs ancilla-free encoding. Use X-conjugation.

        # We implement each SAME pattern as an exact 4-control toggle on anc:
        # A basis state matches exactly one (cu,cv); toggling for each SAME pattern sets anc=1 for SAME.
        same_patterns = [
            (0, 0, 0, 0), (0, 0, 1, 1), (1, 1, 0, 0), (1, 1, 1, 1),  # color0 x color0
            (1, 0, 1, 0),  # (01,01): u0=1,u1=0,v0=1,v1=0
            (0, 1, 0, 1),  # (10,10): u0=0,u1=1,v0=0,v1=1
        ]
        ctrls = [u0, u1, v0, v1]
        for pu0, pu1, pv0, pv1 in same_patterns:
            pat = [pu0, pu1, pv0, pv1]
            for c, want in zip(ctrls, pat):
                if want == 0:
                    qc.x(c)
            qc.mcx(ctrls, anc)
            for c, want in zip(ctrls, pat):
                if want == 0:
                    qc.x(c)
        # Now anc = 1 iff SAME. Invert to get differ (edge ok).
        qc.x(anc)

    def uncompute_edge_ok(u, v, anc):
        u0, u1 = qb(u, 0), qb(u, 1)
        v0, v1 = qb(v, 0), qb(v, 1)
        same_patterns = [
            (0, 0, 0, 0), (0, 0, 1, 1), (1, 1, 0, 0), (1, 1, 1, 1),
            (1, 0, 1, 0),
            (0, 1, 0, 1),
        ]
        ctrls = [u0, u1, v0, v1]
        qc.x(anc)
        for pu0, pu1, pv0, pv1 in reversed(same_patterns):
            pat = [pu0, pu1, pv0, pv1]
            for c, want in zip(ctrls, pat):
                if want == 0:
                    qc.x(c)
            qc.mcx(ctrls, anc)
            for c, want in zip(ctrls, pat):
                if want == 0:
                    qc.x(c)

    # Compute each edge-ok flag.
    for (u, v), anc in zip(edges, edge_anc):
        compute_edge_ok(u, v, anc)

    # Phase -1 iff all edge-ok flags are 1: use multi-controlled Z via final ancilla.
    qc.h(final_anc)
    qc.mcx(edge_anc, final_anc)
    qc.h(final_anc)

    # Uncompute edge flags.
    for (u, v), anc in zip(reversed(edges), reversed(edge_anc)):
        uncompute_edge_ok(u, v, anc)
