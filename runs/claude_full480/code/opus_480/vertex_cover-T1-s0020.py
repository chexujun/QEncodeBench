from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    p = problem_qubits
    edges = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)]

    edge_anc = ancilla_qubits[0:5]   # per-edge coverage flag
    b0 = ancilla_qubits[5]           # popcount bit 0
    b1 = ancilla_qubits[6]           # popcount bit 1
    b2 = ancilla_qubits[7]           # popcount bit 2

    def add_bit(xi):
        qc.mcx([b0, b1, xi], b2)
        qc.ccx(b0, xi, b1)
        qc.cx(xi, b0)

    def add_bit_inv(xi):
        qc.cx(xi, b0)
        qc.ccx(b0, xi, b1)
        qc.mcx([b0, b1, xi], b2)

    def edge_on(u, v, a):
        qc.x(p[u]); qc.x(p[v])
        qc.ccx(p[u], p[v], a)
        qc.x(a)
        qc.x(p[u]); qc.x(p[v])

    def edge_off(u, v, a):
        qc.x(p[u]); qc.x(p[v])
        qc.x(a)
        qc.ccx(p[u], p[v], a)
        qc.x(p[u]); qc.x(p[v])

    # compute
    for (u, v), a in zip(edges, edge_anc):
        edge_on(u, v, a)
    for xi in (p[0], p[1], p[2], p[3]):
        add_bit(xi)

    # phase: mark iff all edges covered AND popcount in {0,1,2}
    # popcount(3 bits b2 b1 b0): accept 000,001,010 ; reject 011(=3),100(=4)
    # => accept iff b2==0 AND NOT(b1 AND b0)
    qc.x(b2)  # now "b2==0" is encoded as b2==1

    # multi-controlled-Z over set S = -1 iff all qubits of S are 1
    def mcz(qubits):
        *ctrls, tgt = qubits
        qc.h(tgt); qc.mcx(ctrls, tgt); qc.h(tgt)

    # term A: edges all 1 AND b2==0  -> phase -1
    mcz(list(edge_anc) + [b2])
    # term B: subtract the wrongly-marked value 3 (edges1, b2==0, b1=1, b0=1): apply again to cancel
    mcz(list(edge_anc) + [b2, b1, b0])

    qc.x(b2)  # restore

    # uncompute
    for xi in (p[3], p[2], p[1], p[0]):
        add_bit_inv(xi)
    for (u, v), a in zip(reversed(edges), reversed(edge_anc)):
        edge_off(u, v, a)
