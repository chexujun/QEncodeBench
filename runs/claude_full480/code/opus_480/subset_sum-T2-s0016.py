from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [8, 8, 10, 3]
    T = 18
    n = len(a)
    maxsum = sum(a)
    nbits = int(np.floor(np.log2(maxsum))) + 1 if maxsum > 0 else 1

    s = ancilla_qubits[:nbits]
    flag = ancilla_qubits[nbits]

    def cinc(ctrl):
        m = len(s)
        for i in range(m - 1, 0, -1):
            qc.mcx([ctrl] + s[0:i], s[i])
        qc.cx(ctrl, s[0])

    def cdec(ctrl):
        m = len(s)
        qc.cx(ctrl, s[0])
        for i in range(1, m):
            qc.mcx([ctrl] + s[0:i], s[i])

    def cadd(const, ctrl):
        for _ in range(const):
            cinc(ctrl)

    def csub(const, ctrl):
        for _ in range(const):
            cdec(ctrl)

    for i in range(n):
        cadd(a[i], problem_qubits[i])

    tbits = [(T >> k) & 1 for k in range(nbits)]
    for k in range(nbits):
        if tbits[k] == 0:
            qc.x(s[k])
    qc.h(flag)
    qc.mcx(s, flag)
    qc.h(flag)
    for k in range(nbits):
        if tbits[k] == 0:
            qc.x(s[k])

    for i in reversed(range(n)):
        csub(a[i], problem_qubits[i])
