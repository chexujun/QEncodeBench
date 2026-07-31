from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 1), (0, 2), (0, 4), (1, 3), (1, 4), (2, 4), (3, 4), (3, 5)]
    n = 6
    p = [problem_qubits[i] for i in range(n)]

    edge_anc = ancilla_qubits[0:8]   # covered-flag per edge
    c0, c1, c2 = ancilla_qubits[8], ancilla_qubits[9], ancilla_qubits[10]

    def compute():
        # edge covered flags: covered = u OR v
        for idx, (u, v) in enumerate(edges):
            a = edge_anc[idx]
            qc.x(p[u]); qc.x(p[v])
            qc.x(a)
            qc.ccx(p[u], p[v], a)   # a = 1 unless both endpoints out -> a = covered
            qc.x(p[u]); qc.x(p[v])
        # popcount into (c2,c1,c0), MSB c2
        for i in range(n):
            b = p[i]
            qc.mcx([b, c0, c1], c2)  # carry into c2
            qc.ccx(b, c0, c1)        # carry into c1
            qc.cx(b, c0)             # add into c0

    def uncompute():
        for i in reversed(range(n)):
            b = p[i]
            qc.cx(b, c0)
            qc.ccx(b, c0, c1)
            qc.mcx([b, c0, c1], c2)
        for idx, (u, v) in enumerate(edges):
            a = edge_anc[idx]
            qc.x(p[u]); qc.x(p[v])
            qc.ccx(p[u], p[v], a)
            qc.x(a)
            qc.x(p[u]); qc.x(p[v])

    compute()

    # f = (all edges covered) AND (count <= 4)
    # count <= 4  <=>  NOT( c2 AND (c1 OR c0) )
    # Disjoint split of the marked set:
    #   term A: all_edges AND NOT c2                      (count 0..3)
    #   term B: all_edges AND c2 AND NOT c1 AND NOT c0    (count == 4)
    # Apply -1 phase on each; disjoint so phases don't interfere.
    ctrls = list(edge_anc)

    # term A: controls = edges..., plus NOT c2  -> phase -1 via multi-controlled Z (last edge as target of Z)
    qc.x(c2)
    qc.h(ctrls[-1])
    qc.mcx(ctrls[:-1] + [c2], ctrls[-1])
    qc.h(ctrls[-1])
    qc.x(c2)

    # term B: controls = edges..., c2, NOT c1, NOT c0
    qc.x(c1); qc.x(c0)
    qc.h(ctrls[-1])
    qc.mcx(ctrls[:-1] + [c2, c1, c0], ctrls[-1])
    qc.h(ctrls[-1])
    qc.x(c1); qc.x(c0)

    uncompute()
