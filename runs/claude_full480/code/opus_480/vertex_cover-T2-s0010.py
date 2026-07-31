from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 2), (0, 4), (1, 2), (1, 4), (2, 4), (3, 4)]
    p = problem_qubits
    n = len(p)

    edge_anc = ancilla_qubits[0:6]
    count_anc = ancilla_qubits[6:9]
    result = ancilla_qubits[8]

    for idx, (u, v) in enumerate(edges):
        a = edge_anc[idx]
        qc.x(p[u])
        qc.x(p[v])
        qc.x(a)
        qc.ccx(p[u], p[v], a)
        qc.x(p[u])
        qc.x(p[v])

    c0, c1 = count_anc[0], count_anc[1]
    for i in range(n):
        qc.ccx(p[i], c0, c1)
        qc.cx(p[i], c0)

    qc.x(result)
    for a in edge_anc:
        qc.cx(a, result)
        qc.x(a)
    qc.mcx(edge_anc, result)
    for a in edge_anc:
        qc.x(a)

    qc.x(result)

    qc.h(result)
    qc.mcx(edge_anc + [c1], result)
    qc.h(result)

    qc.x(result)

    for a in edge_anc:
        qc.x(a)
    qc.mcx(edge_anc, result)
    for a in edge_anc:
        qc.cx(a, result)
        qc.x(a)
    qc.x(result)

    for i in reversed(range(n)):
        qc.cx(p[i], c0)
        qc.ccx(p[i], c0, c1)

    for idx, (u, v) in enumerate(edges):
        a = edge_anc[idx]
        qc.x(p[u])
        qc.x(p[v])
        qc.ccx(p[u], p[v], a)
        qc.x(a)
        qc.x(p[u])
        qc.x(p[v])
