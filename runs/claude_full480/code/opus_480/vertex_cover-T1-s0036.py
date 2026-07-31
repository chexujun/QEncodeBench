from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    edges = [(0, 1), (0, 2), (0, 3), (1, 3)]

    edge_anc = ancilla_qubits[0:4]   # one ancilla per edge (edge covered)
    cover_anc = ancilla_qubits[4]    # all edges covered
    size_anc = ancilla_qubits[5]     # popcount <= 2
    result = ancilla_qubits[6]       # final predicate

    # --- compute: edge covered = OR of endpoints = NOT(AND of negations) ---
    for idx, (u, v) in enumerate(edges):
        qu, qv = problem_qubits[u], problem_qubits[v]
        a = edge_anc[idx]
        # a = x_u OR x_v : start a=1, then a=0 iff both endpoints 0
        qc.x(a)
        qc.x(qu)
        qc.x(qv)
        qc.ccx(qu, qv, a)  # if both were 0, flip a to 0
        qc.x(qu)
        qc.x(qv)

    # cover_anc = AND of all edge_anc (all edges covered)
    qc.mcx(edge_anc, cover_anc)

    # --- compute size_anc = 1 iff popcount(x) <= 2, i.e. NOT(>=3) ---
    # popcount >= 3 over 4 bits means at least 3 of the 4 are 1.
    # The 4 ways to pick 3 ones: complement of each single bit being 0.
    # popcount>=3 <=> exists a triple all ones OR all four ones.
    # Use a temporary marker on 'result' to accumulate "has >=3", then invert.
    # We compute size_anc directly: size_anc starts |0>, set to 1 when popcount<=2.
    # Easier: mark size_anc=1 for popcount>=3, then X to invert.
    triples = [(x1, x2, x3), (x0, x2, x3), (x0, x1, x3), (x0, x1, x2)]
    for a, b, c in triples:
        qc.mcx([a, b, c], size_anc)  # flips for each satisfied triple
    # For popcount==3 exactly one triple satisfied -> size_anc=1.
    # For popcount==4 all four triples satisfied -> flips 4 times -> size_anc=0. Fix:
    qc.mcx([x0, x1, x2, x3], size_anc)  # add flip for all-four -> size_anc=1
    # Now size_anc = 1 iff popcount>=3. Invert so size_anc=1 iff popcount<=2.
    qc.x(size_anc)

    # result = cover_anc AND size_anc
    qc.ccx(cover_anc, size_anc, result)

    # --- phase ---
    qc.z(result)

    # --- uncompute (mirror everything) ---
    qc.ccx(cover_anc, size_anc, result)

    qc.x(size_anc)
    qc.mcx([x0, x1, x2, x3], size_anc)
    for a, b, c in reversed(triples):
        qc.mcx([a, b, c], size_anc)

    qc.mcx(edge_anc, cover_anc)

    for idx in reversed(range(len(edges))):
        u, v = edges[idx]
        qu, qv = problem_qubits[u], problem_qubits[v]
        a = edge_anc[idx]
        qc.x(qu)
        qc.x(qv)
        qc.ccx(qu, qv, a)
        qc.x(qu)
        qc.x(qv)
        qc.x(a)
