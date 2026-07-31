from qiskit import QuantumCircuit
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 1), (0, 2), (1, 2), (1, 3)]

    def vbits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_anc = ancilla_qubits[:4]   # one "edge OK" flag per edge
    out = ancilla_qubits[4]         # final AND flag

    def edge_diff_compute(u, v, anc):
        # anc becomes 1 iff colors(u) != colors(v) after surjective decode
        # colors equal iff codes equal OR one is 00 and other is 11
        # -> decoded-equal set: {(a,a)} union {(00,11),(11,00)}
        # We compute d0 = b0u xor b0v, d1 = b1u xor b1v into temp using anc region? 
        # Instead build "same color" indicator then flip.
        u0, u1 = vbits(u)
        v0, v1 = vbits(v)
        # Decoded color equality predicate S(u,v):
        # equal codes: d0=0 and d1=0
        # 00 vs 11: u=00,v=11 -> d0=1,d1=1 with u1=0 ... need distinguish from 01 vs10 (also d0=1,d1=1)
        # Distinguish: 00&11 pair are the two codes where b0==b1. 01,10 have b0!=b1.
        # For d0=d1=1 case, same-color iff (b0u==b1u) i.e. u is 00 or 11 (then v is the complementary 00/11).
        # Enumerate same-color pairs (cu,cv): decode c: 0->0,1->1,2->2,3->0
        # same when {cu,cv} in: (0,0),(1,1),(2,2),(3,3),(0,3),(3,0)
        # Mark anc=1 for these (same), then X to get diff. Use 4 ccx-based terms.
        # We'll compute using controlled toggles on anc for each same-pair via mcx over 4 controls.
        # Prepare per-vertex code-equality by controlling on bit patterns.
        same_pairs = [(0, 0), (1, 1), (2, 2), (3, 3), (0, 3), (3, 0)]
        controls = [u0, u1, v0, v1]
        for cu, cv in same_pairs:
            pat = [cu & 1, (cu >> 1) & 1, cv & 1, (cv >> 1) & 1]
            for i, p in enumerate(pat):
                if p == 0:
                    qc.x(controls[i])
            qc.mcx(controls, anc)
            for i, p in enumerate(pat):
                if p == 0:
                    qc.x(controls[i])
        qc.x(anc)  # now anc = 1 iff colors differ (edge satisfied)

    def edge_diff_uncompute(u, v, anc):
        u0, u1 = vbits(u)
        v0, v1 = vbits(v)
        same_pairs = [(0, 0), (1, 1), (2, 2), (3, 3), (0, 3), (3, 0)]
        controls = [u0, u1, v0, v1]
        qc.x(anc)
        for cu, cv in reversed(same_pairs):
            pat = [cu & 1, (cu >> 1) & 1, cv & 1, (cv >> 1) & 1]
            for i, p in enumerate(pat):
                if p == 0:
                    qc.x(controls[i])
            qc.mcx(controls, anc)
            for i, p in enumerate(pat):
                if p == 0:
                    qc.x(controls[i])

    # compute all edge flags
    for (u, v), anc in zip(edges, edge_anc):
        edge_diff_compute(u, v, anc)

    # out = AND of all edge flags, phase it
    qc.mcx(edge_anc, out)
    qc.z(out)
    qc.mcx(edge_anc, out)

    # uncompute edge flags
    for (u, v), anc in zip(reversed(edges), reversed(edge_anc)):
        edge_diff_uncompute(u, v, anc)
