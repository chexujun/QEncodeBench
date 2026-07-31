import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3)]
    p = problem_qubits

    edge_anc = ancilla_qubits[0:5]   # one per edge
    all_edges = ancilla_qubits[5]    # AND of all edge-covered flags
    size_ok = ancilla_qubits[6]      # popcount <= 2 flag
    final = ancilla_qubits[7]        # overall predicate

    # ---- compute: each edge covered = OR of its two endpoints ----
    for (u, v), a in zip(edges, edge_anc):
        # OR(u,v) into a: a = u OR v  =  NOT( NOT u AND NOT v )
        qc.x(p[u]); qc.x(p[v])
        qc.x(a)
        qc.ccx(p[u], p[v], a)   # a = 1 - (nu AND nv) = u OR v
        qc.x(p[u]); qc.x(p[v])

    # all edges covered
    qc.mcx(edge_anc, all_edges)

    # ---- compute: size_ok = (popcount(x) <= 2) ----
    # popcount over 4 bits <= 2  is FALSE only when >=3 ones set,
    # i.e. at least one of the C(4,3)=4 triples is all-ones... actually
    # popcount>=3 means at least 3 ones. Equivalent: NOT( any triple all ones ).
    # size_ok = 1 unless (three or four bits set).
    # Mark "bad size" into size_ok then invert.
    triples = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    # size_ok starts |0>; set size_ok=1 if any triple all ones (bad), then flip.
    for (i, j, k) in triples:
        qc.mcx([p[i], p[j], p[k]], size_ok)
    # Now size_ok = XOR over triples of (triple all ones).
    # If exactly 3 bits set: exactly one triple true -> size_ok=1.
    # If 4 bits set: all 4 triples true -> XOR = 0. Fix that case:
    # add correction: when all 4 set, flip size_ok back to 1.
    qc.mcx([p[0], p[1], p[2], p[3]], size_ok)
    # Now size_ok = 1 iff popcount >= 3 (bad). Invert to get "<=2 good".
    qc.x(size_ok)

    # ---- final = all_edges AND size_ok ----
    qc.ccx(all_edges, size_ok, final)

    # ---- phase ----
    qc.z(final)

    # ---- uncompute (mirror) ----
    qc.ccx(all_edges, size_ok, final)

    qc.x(size_ok)
    qc.mcx([p[0], p[1], p[2], p[3]], size_ok)
    for (i, j, k) in reversed(triples):
        qc.mcx([p[i], p[j], p[k]], size_ok)

    qc.mcx(edge_anc, all_edges)

    for (u, v), a in zip(reversed(edges), reversed(edge_anc)):
        qc.x(p[u]); qc.x(p[v])
        qc.ccx(p[u], p[v], a)
        qc.x(a)
        qc.x(p[u]); qc.x(p[v])
