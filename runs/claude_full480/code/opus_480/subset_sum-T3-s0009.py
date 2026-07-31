from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    a = [3, 14, 3, 13, 3]
    T = 6
    nbits = 4  # sums up to 3+14+3+13+3=36 < 64, but 6 bits safe; use 4 -> need up to 36 -> 6 bits
    nbits = 6
    s = ancilla_qubits[:nbits]  # 6-bit accumulator register

    def add_constant(const, control):
        # add `const` into register s, controlled on `control`, in place (ripple, no extra ancilla)
        for j in range(nbits - 1, -1, -1):
            if (const >> j) & 1:
                for k in range(nbits - 1, j, -1):
                    ctrls = [control] + s[j:k]
                    qc.mcx(ctrls, s[k])
                qc.ccx(control, s[j], s[j]) if False else qc.cx(control, s[j])

    def add_constant_inv(const, control):
        for j in range(0, nbits):
            if (const >> j) & 1:
                qc.cx(control, s[j])
                for k in range(j + 1, nbits):
                    ctrls = [control] + s[j:k]
                    qc.mcx(ctrls, s[k])

    # compute: accumulate selected values
    for i in range(len(a)):
        add_constant(a[i], problem_qubits[i])

    # phase: -1 iff register == T
    tbits = [(T >> j) & 1 for j in range(nbits)]
    for j in range(nbits):
        if not tbits[j]:
            qc.x(s[j])
    if nbits == 1:
        qc.z(s[0])
    else:
        qc.h(s[nbits - 1])
        qc.mcx(s[:nbits - 1], s[nbits - 1])
        qc.h(s[nbits - 1])
    for j in range(nbits):
        if not tbits[j]:
            qc.x(s[j])

    # uncompute
    for i in range(len(a) - 1, -1, -1):
        add_constant_inv(a[i], problem_qubits[i])
