from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    edges = [(0, 1), (1, 3), (2, 3)]

    # Ancilla assignment
    e_anc = ancilla_qubits[0:3]      # one ancilla per edge (edge covered flag)
    cov_anc = ancilla_qubits[3]      # all edges covered
    cnt_anc = ancilla_qubits[4]      # size <= 2 flag
    res_anc = ancilla_qubits[5]      # final predicate

    pq = [x0, x1, x2, x3]

    # ---- compute edge-covered flags: e_anc[i] = u OR v = NOT(NOT u AND NOT v) ----
    for i, (u, v) in enumerate(edges):
        qu, qv = pq[u], pq[v]
        qc.x(qu)
        qc.x(qv)
        qc.ccx(qu, qv, e_anc[i])   # e = (NOT u AND NOT v)
        qc.x(e_anc[i])             # e = u OR v
        qc.x(qu)
        qc.x(qv)

    # ---- all edges covered: cov_anc = AND of e_anc ----
    qc.mcx(e_anc, cov_anc)

    # ---- count constraint: popcount(x) <= 2, i.e. NOT(popcount >= 3) ----
    # popcount>=3 over 4 bits means at least 3 ones. Compute cnt_anc = 1 iff popcount<=2.
    # popcount>=3 iff there exist 3 of the 4 bits set. Enumerate the four 3-subsets;
    # but we avoid baking solutions: use symmetric detection of >=3 ones.
    # >=3 ones == (at least 3 set). Detect via: mark cnt_anc when popcount>=3, then invert.
    # The four ways to have >=3 ones are the four C(4,3) triples; popcount==4 covered by all.
    triples = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    for (a, b, c) in triples:
        qc.mcx([pq[a], pq[b], pq[c]], cnt_anc)  # toggles: parity of satisfied triples
    # For popcount==3 exactly one triple is satisfied -> cnt=1.
    # For popcount==4 all four triples satisfied -> parity 0 -> cnt=0 (WRONG), fix below.
    # Add 4-way term to correct parity for popcount==4.
    qc.mcx([pq[0], pq[1], pq[2], pq[3]], cnt_anc)
    # Now cnt_anc = 1 iff popcount in {3} XOR ... let's verify: pc=4 -> triples give 4 toggles=0, plus 4-term=1 => cnt=1. Good (>=3).
    # pc=3 -> 1 triple toggle=1, 4-term=0 => cnt=1. Good. pc<=2 -> 0 => cnt=0. So cnt_anc=1 iff popcount>=3.
    qc.x(cnt_anc)  # now cnt_anc = 1 iff popcount <= 2

    # ---- predicate = cov_anc AND cnt_anc ----
    qc.ccx(cov_anc, cnt_anc, res_anc)

    # ---- phase ----
    qc.z(res_anc)

    # ---- uncompute (mirror) ----
    qc.ccx(cov_anc, cnt_anc, res_anc)

    qc.x(cnt_anc)
    qc.mcx([pq[0], pq[1], pq[2], pq[3]], cnt_anc)
    for (a, b, c) in reversed(triples):
        qc.mcx([pq[a], pq[b], pq[c]], cnt_anc)

    qc.mcx(e_anc, cov_anc)

    for i in reversed(range(len(edges))):
        u, v = edges[i]
        qu, qv = pq[u], pq[v]
        qc.x(qu)
        qc.x(qv)
        qc.x(e_anc[i])
        qc.ccx(qu, qv, e_anc[i])
        qc.x(qu)
        qc.x(qv)
