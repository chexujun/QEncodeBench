from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [6, 5, 9, 6]
    T = 12
    n = len(a)
    W = max(T, sum(a))
    nbits = W.bit_length()

    s = ancilla_qubits[:nbits]
    flag = ancilla_qubits[nbits]

    def add_constant(const, ctrl):
        # controlled add of `const` into register s (little-endian), ctrl is control qubit
        for shift in range(nbits):
            if (const >> shift) & 1:
                for j in range(nbits - 1, shift - 1, -1):
                    controls = [ctrl] + [s[k] for k in range(shift, j)]
                    qc.mcx(controls, s[j])

    def subtract_constant(const, ctrl):
        for shift in range(nbits):
            if (const >> shift) & 1:
                for j in range(shift, nbits):
                    controls = [ctrl] + [s[k] for k in range(shift, j)]
                    qc.mcx(controls, s[j])

    # compute sum of selected elements into s
    for i in range(n):
        add_constant(a[i], problem_qubits[i])

    # mark flag if s == T
    Tbits = [(T >> k) & 1 for k in range(nbits)]
    for k in range(nbits):
        if Tbits[k] == 0:
            qc.x(s[k])
    qc.mcx([s[k] for k in range(nbits)], flag)
    for k in range(nbits):
        if Tbits[k] == 0:
            qc.x(s[k])

    # phase
    qc.z(flag)

    # unmark flag
    for k in range(nbits):
        if Tbits[k] == 0:
            qc.x(s[k])
    qc.mcx([s[k] for k in range(nbits)], flag)
    for k in range(nbits):
        if Tbits[k] == 0:
            qc.x(s[k])

    # uncompute sum
    for i in range(n - 1, -1, -1):
        subtract_constant(a[i], problem_qubits[i])
