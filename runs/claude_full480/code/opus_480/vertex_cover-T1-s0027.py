from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Problem: vertex cover of graph with edges (0,1),(0,2),(0,3), size <= 2.
    # x_i = 1 means vertex i in cover.
    # f(x)=1 iff every edge covered AND popcount(x) <= 2.
    v0, v1, v2, v3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]

    # Ancilla roles:
    #  e0,e1,e2 : edge-covered flags for edges (0,1),(0,2),(0,3)
    #  cover_ok : AND of the three edge flags
    #  cnt_ok   : popcount(x) <= 2  flag
    #  result   : final predicate (phase target)
    e0, e1, e2 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]
    cover_ok = ancilla_qubits[3]
    cnt_ok = ancilla_qubits[4]
    result = ancilla_qubits[5]

    # ---- compute edge-covered flags ----
    # edge (a,b) covered iff xa OR xb == NOT(NOT xa AND NOT xb).
    # compute e = xa OR xb using: e=1; then if both zero set e=0.
    def edge_or(a, b, e):
        qc.x(a); qc.x(b)
        qc.x(e)
        qc.ccx(a, b, e)   # e = 1 XOR (NOT a AND NOT b) = a OR b
        qc.x(a); qc.x(b)

    edge_or(v0, v1, e0)
    edge_or(v0, v2, e1)
    edge_or(v0, v3, e2)

    # cover_ok = e0 AND e1 AND e2
    qc.mcx([e0, e1, e2], cover_ok)

    # ---- compute cnt_ok = (popcount <= 2) = NOT(popcount >= 3) ----
    # popcount >= 3 among 4 bits means at least 3 ones.
    # The 4-bit strings with >=3 ones: any 3-subset AND the all-4.
    # popcount>=3 iff at least one of the C(4,3)=4 triples is all-ones
    # (all-4 case is covered by any triple). Compute into cnt_ok as
    # NOT(OR of the four triple-AND terms).
    # Use result temporarily? No: build directly.
    # We set cnt_ok = 1, then flip to 0 if any triple all ones. But OR of
    # overlapping ANDs can't be done by simple XOR (double counting).
    # Instead: popcount>=3 is monotone; enumerate exact via the fact that
    # >=3 ones <=> NOT(at most 2 ones). We instead directly test the 5
    # "bad" strings (>=3 ones) individually with multi-controls onto cnt_ok
    # using XOR, since those 5 basis states are mutually exclusive.
    triples = [(v0, v1, v2), (v0, v1, v3), (v0, v2, v3), (v1, v2, v3)]
    # exact-3 patterns: three specific ones, the remaining bit zero.
    all_bits = [v0, v1, v2, v3]
    # exactly-3: for each excluded bit, the other three are 1 and it is 0
    for excl in all_bits:
        ones = [b for b in all_bits if b != excl]
        qc.x(excl)
        qc.mcx(ones + [excl], result)  # wait need controls = ones AND NOT excl
        qc.x(excl)
    # exactly-4: all ones
    qc.mcx(all_bits, result)
    # now `result` holds parity-XOR of the 5 mutually-exclusive bad states
    # = 1 iff popcount>=3. Since they are mutually exclusive, XOR == OR.
    # cnt_ok = NOT result
    qc.x(result)
    qc.cx(result, cnt_ok)   # cnt_ok = NOT(popcount>=3) = (popcount<=2)
    qc.x(result)
    # uncompute result back to 0 (mirror of the bad-state marking)
    qc.mcx(all_bits, result)
    for excl in all_bits:
        ones = [b for b in all_bits if b != excl]
        qc.x(excl)
        qc.mcx(ones + [excl], result)
        qc.x(excl)

    # ---- final predicate = cover_ok AND cnt_ok, apply phase ----
    qc.h(result)
    qc.ccx(cover_ok, cnt_ok, result)  # not needed for phase; use mcp instead
    qc.ccx(cover_ok, cnt_ok, result)
    qc.h(result)
    # The above pair cancels; do the phase cleanly with a controlled-Z:
    qc.h(cnt_ok)
    qc.h(cnt_ok)
    # Apply -1 phase when cover_ok AND cnt_ok both 1:
    qc.mcp(math.pi, [cover_ok], cnt_ok)

    # ---- uncompute cnt_ok ----
    qc.mcx(all_bits, result)
    for excl in all_bits:
        ones = [b for b in all_bits if b != excl]
        qc.x(excl)
        qc.mcx(ones + [excl], result)
        qc.x(excl)
    qc.x(result)
    qc.cx(result, cnt_ok)
    qc.x(result)
    qc.mcx(all_bits, result)
    for excl in all_bits:
        ones = [b for b in all_bits if b != excl]
        qc.x(excl)
        qc.mcx(ones + [excl], result)
        qc.x(excl)

    # ---- uncompute cover_ok ----
    qc.mcx([e0, e1, e2], cover_ok)

    # ---- uncompute edge flags ----
    edge_or(v0, v3, e2)
    edge_or(v0, v2, e1)
    edge_or(v0, v1, e0)
