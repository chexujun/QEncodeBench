import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (0, 4), (0, 5), (1, 4), (1, 5),
             (2, 4), (2, 5), (3, 4), (3, 5)]
    p = problem_qubits
    n = len(edges)

    # edge ancillas: one per edge, set to 1 iff edge is covered
    edge_anc = ancilla_qubits[:n]          # 10 ancillas
    all_cov = ancilla_qubits[n]            # 1 ancilla: all edges covered
    weight_ok = ancilla_qubits[n + 1]      # 1 ancilla: popcount(x) <= 3
    final = ancilla_qubits[n + 2]          # 1 ancilla: predicate flag

    # ---- compute edge coverage: edge_anc[i] = u OR v ----
    def cover_compute():
        for i, (u, v) in enumerate(edges):
            a = edge_anc[i]
            qc.x(p[u]); qc.x(p[v])
            qc.x(a)
            qc.ccx(p[u], p[v], a)   # a = 1 iff not(u=0 and v=0) = u OR v
            qc.x(p[u]); qc.x(p[v])

    def cover_uncompute():
        for i, (u, v) in enumerate(edges):
            a = edge_anc[i]
            qc.x(p[u]); qc.x(p[v])
            qc.ccx(p[u], p[v], a)
            qc.x(a)
            qc.x(p[u]); qc.x(p[v])

    # ---- weight_ok = 1 iff popcount(p) <= 3 ----
    # equivalently NOT( at least 4 of the 6 bits set ).
    # Use a small sum register via reversible increments comparing threshold.
    # We compute predicate: number of ones <= 3 for 6 bits.
    # Build using a 3-bit counter in scratch ancillas is heavy; instead
    # test the complementary condition directly:
    # popcount<=3  <=>  NOT exists a 4-subset all ones.
    # We implement counter with 3 bits reused from the fact that we have
    # spare ancillas? We only have edge_anc free after uncompute, but we
    # need coverage AND weight simultaneously. So compute weight first into
    # weight_ok using a counter built from edge_anc (free before coverage).

    # Counter using 3 bits stored in edge_anc[0..2] as scratch, BEFORE
    # coverage compute. bits c2 c1 c0 = popcount.
    c = [edge_anc[0], edge_anc[1], edge_anc[2]]

    def count_add(bit):
        # add 'bit' (a problem qubit) into 3-bit counter c[0]=lsb
        # carry chain
        qc.ccx(bit, c[0], c[1])
        qc.ccx(bit, c[1], c[2])  # note ordering: apply higher carries first
        qc.cx(bit, c[0])

    def count_add_correct(bit):
        # proper controlled increment: from MSB down for carries
        qc.ccx(c[0], c[1], c[2])
        qc.ccx(bit, c[1], c[2])  # placeholder, replaced below
    # We instead implement a clean increment.

    def increment(ctrl):
        # increment 3-bit counter c by 1, controlled on ctrl
        # carry: if c0 and c1 set, flip c2
        qc.mcx([ctrl, c[0], c[1]], c[2])
        qc.ccx(ctrl, c[0], c[1])
        qc.cx(ctrl, c[0])

    def increment_inv(ctrl):
        qc.cx(ctrl, c[0])
        qc.ccx(ctrl, c[0], c[1])
        qc.mcx([ctrl, c[0], c[1]], c[2])

    # compute popcount
    for i in range(6):
        increment(p[i])
    # popcount<=3 means c2c1c0 <= 011, i.e. value in {0,1,2,3} -> c2==0.
    # Because max count is 6 (110). c2==0 covers 0..3; c2==1 covers 4,5,6,7.
    # But value 3 = 011 -> c2=0 good; value 4=100 -> c2=1. Exactly threshold.
    qc.x(c[2])
    qc.cx(c[2], weight_ok)   # weight_ok = NOT c2 = (popcount<=3)
    qc.x(c[2])
    # uncompute popcount
    for i in reversed(range(6)):
        increment_inv(p[i])

    # ---- compute coverage flags ----
    cover_compute()

    # all_cov = AND of all edge_anc
    qc.mcx(edge_anc, all_cov)

    # final = all_cov AND weight_ok
    qc.ccx(all_cov, weight_ok, final)

    # phase
    qc.z(final)

    # uncompute final, all_cov
    qc.ccx(all_cov, weight_ok, final)
    qc.mcx(edge_anc, all_cov)

    cover_uncompute()

    # uncompute weight_ok
    for i in range(6):
        increment(p[i])
    qc.x(c[2])
    qc.cx(c[2], weight_ok)
    qc.x(c[2])
    for i in reversed(range(6)):
        increment_inv(p[i])
