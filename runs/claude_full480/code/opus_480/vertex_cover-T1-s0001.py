import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    edges = [(0, 1), (0, 2), (2, 3)]

    # ancilla layout
    e0, e1, e2 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]
    cov = ancilla_qubits[3]      # all-edges-covered flag
    cnt_ok = ancilla_qubits[4]   # popcount <= 2 flag
    res = ancilla_qubits[5]      # final predicate flag

    edge_anc = [e0, e1, e2]
    ev = problem_qubits

    # ---- compute: each edge covered flag = OR(u, v) = NOT(AND(NOT u, NOT v))
    for (u, v), a in zip(edges, edge_anc):
        qu, qv = ev[u], ev[v]
        qc.x(qu)
        qc.x(qv)
        qc.ccx(qu, qv, a)   # a = (not u) and (not v) = edge NOT covered
        qc.x(qu)
        qc.x(qv)
        qc.x(a)             # a = edge covered

    # cov = AND of all edge flags
    qc.mcx([e0, e1, e2], cov)

    # ---- compute count <= 2 : true unless popcount(x) >= 3
    # popcount >= 3 over 4 bits means at least 3 ones.
    # cnt_ok = NOT( at least 3 ones )
    # at least 3 ones = OR over all C(4,3) triples of AND of that triple
    #   (any 3-subset all ones). If any triple all-ones -> >=3 ones.
    # We compute "bad" (>=3 ones) into cnt_ok via inclusion using res as temp.
    # Simpler: mark bad if sum>=3. Enumerate triples into cnt_ok using OR.
    triples = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    # OR of triple-ANDs: start cnt_ok=0 (means good). Set bad flag on res temp.
    # Use res as running OR of bad condition.
    for (a, b, c) in triples:
        qc.mcx([ev[a], ev[b], ev[c]], cnt_ok)  # toggles; but overlaps cause issues
    # Fix overlap: mcx toggles cnt_ok once per satisfied triple.
    # For popcount==3 exactly one triple satisfied -> cnt_ok=1 (bad).
    # For popcount==4 all four triples satisfied -> toggled 4 times -> cnt_ok=0 (wrong!).
    # Handle popcount==4 separately: all four bits one.
    qc.mcx([ev[0], ev[1], ev[2], ev[3]], cnt_ok)  # for popcount4: +1 -> total 5 toggles=1 (bad). good.

    # now cnt_ok==1 means BAD (count>=3), cnt_ok==0 means good (count<=2)
    qc.x(cnt_ok)  # now cnt_ok==1 means count<=2 (good)

    # ---- res = cov AND cnt_ok
    qc.ccx(cov, cnt_ok, res)

    # ---- phase
    qc.z(res)

    # ---- uncompute (mirror)
    qc.ccx(cov, cnt_ok, res)

    qc.x(cnt_ok)
    qc.mcx([ev[0], ev[1], ev[2], ev[3]], cnt_ok)
    for (a, b, c) in reversed(triples):
        qc.mcx([ev[a], ev[b], ev[c]], cnt_ok)

    qc.mcx([e0, e1, e2], cov)

    for (u, v), a in zip(reversed(edges), reversed(edge_anc)):
        qu, qv = ev[u], ev[v]
        qc.x(a)
        qc.x(qu)
        qc.x(qv)
        qc.ccx(qu, qv, a)
        qc.x(qu)
        qc.x(qv)
