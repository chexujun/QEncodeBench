from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [14, 4, 12, 8, 7]
    T = 12
    n = len(a)
    W = max(T, sum(a))
    nbits = W.bit_length()

    s = ancilla_qubits[0:nbits]
    flag = ancilla_qubits[nbits]

    def add_constant(const, qubits):
        m = len(qubits)
        for j in range(m - 1, -1, -1):
            for k in range(m - 1, j - 1, -1):
                angle = np.pi * const / (2 ** (k - j))
                qc.p(angle, qubits[j])

    def cadd_constant(ctrl, const, qubits):
        m = len(qubits)
        for j in range(m - 1, -1, -1):
            for k in range(m - 1, j - 1, -1):
                angle = np.pi * const / (2 ** (k - j))
                qc.cp(angle, ctrl, qubits[j])

    def qft(qubits):
        m = len(qubits)
        for j in range(m - 1, -1, -1):
            qc.h(qubits[j])
            for k in range(j - 1, -1, -1):
                qc.cp(np.pi / (2 ** (j - k)), qubits[k], qubits[j])

    def iqft(qubits):
        m = len(qubits)
        for j in range(m):
            for k in range(j):
                qc.cp(-np.pi / (2 ** (j - k)), qubits[k], qubits[j])
            qc.h(qubits[j])

    def compute_sum():
        qft(s)
        for i in range(n):
            cadd_constant(problem_qubits[i], a[i], s)
        iqft(s)

    def uncompute_sum():
        qft(s)
        for i in range(n):
            cadd_constant(problem_qubits[i], -a[i], s)
        iqft(s)

    # compute the subset sum into register s
    compute_sum()

    # flip flag iff s == T, phase it, unflip
    Tbits = [(T >> b) & 1 for b in range(nbits)]
    for b in range(nbits):
        if Tbits[b] == 0:
            qc.x(s[b])
    qc.mcx(s, flag)
    qc.z(flag)
    qc.mcx(s, flag)
    for b in range(nbits):
        if Tbits[b] == 0:
            qc.x(s[b])

    # uncompute the subset sum
    uncompute_sum()
