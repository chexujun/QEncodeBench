from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    v = problem_qubits
    edges = [(0, 1), (1, 2), (2, 4), (3, 4)]

    edge_anc = ancilla_qubits[0:4]
    count_anc = ancilla_qubits[4:7]
    all_ok = None

    def compute_edges():
        for idx, (i, j) in enumerate(edges):
            a = edge_anc[idx]
            qc.x(v[i]); qc.x(v[j])
            qc.x(a)
            qc.ccx(v[i], v[j], a)
            qc.x(v[i]); qc.x(v[j])

    def uncompute_edges():
        for idx, (i, j) in enumerate(edges):
            a = edge_anc[idx]
            qc.x(v[i]); qc.x(v[j])
            qc.ccx(v[i], v[j], a)
            qc.x(a)
            qc.x(v[i]); qc.x(v[j])

    def add_bit(control, c0, c1, c2):
        qc.ccx(control, c1, c2)
        qc.ccx(control, c0, c1)
        qc.cx(control, c0)

    def unadd_bit(control, c0, c1, c2):
        qc.cx(control, c0)
        qc.ccx(control, c0, c1)
        qc.ccx(control, c1, c2)

    def compute_count():
        for i in range(5):
            add_bit(v[i], count_anc[0], count_anc[1], count_anc[2])

    def uncompute_count():
        for i in reversed(range(5)):
            unadd_bit(v[i], count_anc[0], count_anc[1], count_anc[2])

    compute_edges()
    compute_count()

    qc.x(count_anc[1])
    qc.x(count_anc[2])
    qc.mcp(pi, edge_anc + [count_anc[1]], count_anc[2])
    qc.x(count_anc[1])
    qc.x(count_anc[2])

    uncompute_count()
    uncompute_edges()
