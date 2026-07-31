from qiskit import QuantumCircuit
from math import pi


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    v0, v1, v2, v3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    # Ancillas: 3 edge ancillas, 1 count-ok ancilla, 1 final predicate ancilla, 1 scratch
    e_a = ancilla_qubits[0]   # edge (0,2) covered
    e_b = ancilla_qubits[1]   # edge (0,3) covered
    e_c = ancilla_qubits[2]   # edge (1,3) covered
    cov = ancilla_qubits[3]   # all edges covered
    cnt = ancilla_qubits[4]   # popcount <= 2
    fin = ancilla_qubits[5]   # final predicate

    # ---- compute edge-covered flags: e = v_i OR v_j = NOT(NOT v_i AND NOT v_j) ----
    def edge_cover(a, b, e):
        qc.x(a); qc.x(b)
        qc.ccx(a, b, e)   # e = (NOT a) AND (NOT b)  -> uncovered
        qc.x(a); qc.x(b)
        qc.x(e)           # e = covered
    edge_cover(v0, v2, e_a)
    edge_cover(v0, v3, e_b)
    edge_cover(v1, v3, e_c)

    # cov = e_a AND e_b AND e_c  (all edges covered)
    qc.mcx([e_a, e_b, e_c], cov)

    # ---- compute count-ok: popcount(v0..v3) <= 2, i.e. NOT(>=3) ----
    # (>=3) means at least 3 of the 4 bits are 1. The 4 triples of the 4 vars:
    # Set cnt = 1 initially (means "ok"), flip to 0 if any triple all-ones.
    qc.x(cnt)  # cnt = 1 (ok)
    # For each 3-subset, if all three are 1 then popcount>=3 -> not ok.
    # mcx toggles cnt; but multiple triples can fire for the same state (e.g. all four =1
    # fires all four triples -> toggles cnt 4 times -> back to 1, WRONG).
    # To avoid that, use a scratch flag OR-reduction instead. Reuse fin as scratch here
    # is unsafe (needed later). Instead detect >=3 via: sum>=3 iff at least three ones.
    # Compute via a robust OR of the four triples into cnt using controlled logic that
    # sets cnt->0 and stays 0. Use ancilla-free trick: flip only when triple holds AND
    # cnt still 1. That requires the current cnt as control (would entangle). Simpler:
    # since exactly the states with >=3 ones must be excluded, and for 4 bits the
    # >=3 set = {0111? no}. List: three-ones (four states) and four-ones (one state).
    # Use a single mcx per triple but guard four-ones by also toggling once more.
    # Cleaner: cnt_notok = OR of triples. Build OR with De Morgan on a scratch is hard
    # with one qubit. Instead: number of triples satisfied = C(popcount,3):
    #   popcount<=2 -> 0 triples; popcount3 -> 1 triple; popcount4 -> 4 triples.
    # Parity of triples: pc3->1 (odd), pc4->4 (even). So parity toggling misses pc4.
    # Fix: add the 4-way mcx (all four ones) to correct pc4 back to odd count.
    triples = [(v0, v1, v2), (v0, v1, v3), (v0, v2, v3), (v1, v2, v3)]
    for t in triples:
        qc.mcx(list(t), cnt)          # toggles cnt for each satisfied triple
    qc.mcx([v0, v1, v2, v3], cnt)     # extra toggle so pc4 nets to odd like pc3
    # Now cnt was set to 1, then toggled: pc<=2 -> 0 toggles -> cnt=1 (ok);
    # pc3 -> 1 toggle -> cnt=0 (not ok); pc4 -> 4+1=5 toggles -> cnt=0 (not ok). Good.

    # ---- final predicate: fin = cov AND cnt ----
    qc.ccx(cov, cnt, fin)

    # ---- phase ----
    qc.z(fin)

    # ---- uncompute (mirror) ----
    qc.ccx(cov, cnt, fin)

    qc.mcx([v0, v1, v2, v3], cnt)
    for t in reversed(triples):
        qc.mcx(list(t), cnt)
    qc.x(cnt)

    qc.mcx([e_a, e_b, e_c], cov)

    def edge_uncover(a, b, e):
        qc.x(e)
        qc.x(a); qc.x(b)
        qc.ccx(a, b, e)
        qc.x(a); qc.x(b)
    edge_uncover(v1, v3, e_c)
    edge_uncover(v0, v3, e_b)
    edge_uncover(v0, v2, e_a)
