import numpy as np
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [6, 5, 12, 6, 6]
    T = 24
    n = len(a)
    maxsum = sum(a)
    nbits = maxsum.bit_length()  # number of ancilla bits to hold the running sum

    reg = ancilla_qubits[:nbits]

    def add_constant(c, ctrl):
        # controlled (on ctrl) addition of classical constant c into reg (little-endian)
        for j in range(nbits):
            if (c >> j) & 1:
                for k in range(nbits - 1, j - 1, -1):
                    controls = [ctrl] + reg[j:k]
                    qc.mcx(controls, reg[k])

    def sub_constant(c, ctrl):
        # inverse of add_constant: mirror order
        for j in range(nbits - 1, -1, -1):
            if (c >> j) & 1:
                for k in range(j, nbits):
                    controls = [ctrl] + reg[j:k]
                    qc.mcx(controls, reg[k])

    # compute: reg = sum of selected a[i]
    for i in range(n):
        add_constant(a[i], problem_qubits[i])

    # phase: -1 iff reg == T
    tbits = [(T >> j) & 1 for j in range(nbits)]
    for j in range(nbits):
        if tbits[j] == 0:
            qc.x(reg[j])
    qc.h(reg[nbits - 1])
    qc.mcx(reg[:nbits - 1], reg[nbits - 1])
    qc.h(reg[nbits - 1])
    for j in range(nbits):
        if tbits[j] == 0:
            qc.x(reg[j])

    # uncompute: reverse the addition
    for i in range(n - 1, -1, -1):
        sub_constant(a[i], problem_qubits[i])
