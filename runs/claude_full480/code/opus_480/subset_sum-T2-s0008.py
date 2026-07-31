import numpy as np
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [9, 8, 2, 10]
    T = 27
    n = len(a)
    maxsum = sum(a)
    nbits = maxsum.bit_length()

    reg = ancilla_qubits[:nbits]
    flag = ancilla_qubits[nbits]

    def add_constant(const, ctrl):
        c = const
        for j in range(nbits):
            if (c >> j) & 1:
                for k in range(nbits - 1, j - 1, -1):
                    controls = [ctrl] + reg[j:k]
                    qc.mcx(controls, reg[k])

    def uncompute_constant(const, ctrl):
        c = const
        for j in range(nbits - 1, -1, -1):
            if (c >> j) & 1:
                for k in range(j, nbits):
                    controls = [ctrl] + reg[j:k]
                    qc.mcx(controls, reg[k])

    for i in range(n):
        add_constant(a[i], problem_qubits[i])

    for j in range(nbits):
        if not ((T >> j) & 1):
            qc.x(reg[j])

    qc.mcx(reg[:nbits], flag)
    qc.z(flag)
    qc.mcx(reg[:nbits], flag)

    for j in range(nbits):
        if not ((T >> j) & 1):
            qc.x(reg[j])

    for i in range(n - 1, -1, -1):
        uncompute_constant(a[i], problem_qubits[i])
