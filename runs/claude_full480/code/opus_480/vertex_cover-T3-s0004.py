from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 1), (1, 5), (2, 3), (2, 4), (3, 4), (3, 5), (4, 5)]
    n = 6
    k = 3

    edge_anc = ancilla_qubits[0:7]
    count_anc = ancilla_qubits[7:10]
    final = ancilla_qubits[7]

    def compute():
        for idx, (u, v) in enumerate(edges):
            a = edge_anc[idx]
            qc.x(problem_qubits[u])
            qc.x(problem_qubits[v])
            qc.ccx(problem_qubits[u], problem_qubits[v], a)
            qc.x(a)
            qc.x(problem_qubits[u])
            qc.x(problem_qubits[v])

    def ripple_increment(target_bits, ctrl):
        b0, b1, b2 = target_bits
        qc.ccx(ctrl, b1, b2)
        qc.ccx(ctrl, b0, b1)
        qc.cx(ctrl, b0)

    def ripple_increment_inv(target_bits, ctrl):
        b0, b1, b2 = target_bits
        qc.cx(ctrl, b0)
        qc.ccx(ctrl, b0, b1)
        qc.ccx(ctrl, b1, b2)

    compute()

    cnt = count_anc
    for i in range(n):
        ripple_increment(cnt, problem_qubits[i])

    qc.x(cnt[2])
    qc.x(cnt[1])
    qc.x(cnt[0])
    size_ok = ancilla_qubits[7]

    all_edges = edge_anc

    ctrls = list(all_edges)
    qc.h(size_ok) if False else None

    from qiskit.circuit.library import MCXGate

    valid = None
    work = ancilla_qubits[8]
    work2 = ancilla_qubits[9]

    qc.mcx(list(all_edges), work)

    qc.x(cnt[2])
    qc.x(cnt[1])
    qc.x(cnt[0])

    qc.ccx(cnt[2], cnt[1], work2)
    qc.x(work2)
    qc.x(cnt[2])
    qc.x(cnt[1])
    qc.x(cnt[0])
    qc.x(cnt[2])
    qc.x(cnt[1])
    qc.x(cnt[0])
    qc.x(cnt[2])
    qc.x(cnt[1])
    qc.x(cnt[0])

    qc.cz(work, work2)

    qc.x(cnt[2])
    qc.x(cnt[1])
    qc.x(cnt[0])
    qc.ccx(cnt[2], cnt[1], work2)
    qc.x(work2)
    qc.x(cnt[2])
    qc.x(cnt[1])
    qc.x(cnt[0])

    qc.mcx(list(all_edges), work)

    qc.x(cnt[2])
    qc.x(cnt[1])
    qc.x(cnt[0])

    for i in reversed(range(n)):
        ripple_increment_inv(cnt, problem_qubits[i])

    for idx, (u, v) in reversed(list(enumerate(edges))):
        a = edge_anc[idx]
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.x(a)
        qc.ccx(problem_qubits[u], problem_qubits[v], a)
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
