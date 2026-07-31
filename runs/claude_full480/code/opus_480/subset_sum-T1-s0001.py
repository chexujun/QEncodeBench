from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    a = [5, 5, 5]
    T = 10
    n = len(a)
    maxsum = sum(a)
    nbits = max(1, int(np.floor(np.log2(maxsum))) + 1) if maxsum > 0 else 1

    sum_anc = ancilla_qubits[:nbits]
    flag = ancilla_qubits[nbits]

    def add_constant(const, ctrl):
        for b in range(nbits):
            if (const >> b) & 1:
                for j in range(nbits - 1, b, -1):
                    controls = [ctrl] + sum_anc[b:j]
                    qc.mcx(controls, sum_anc[j])
                qc.cx(ctrl, sum_anc[b])

    def add_constant_inv(const, ctrl):
        for b in range(nbits):
            if (const >> b) & 1:
                qc.cx(ctrl, sum_anc[b])
                for j in range(b + 1, nbits):
                    controls = [ctrl] + sum_anc[b:j]
                    qc.mcx(controls, sum_anc[j])

    for i in range(n):
        add_constant(a[i], problem_qubits[i])

    tbits = [(T >> b) & 1 for b in range(nbits)]
    for b in range(nbits):
        if tbits[b] == 0:
            qc.x(sum_anc[b])
    qc.mcx(sum_anc, flag)
    qc.z(flag)
    qc.mcx(sum_anc, flag)
    for b in range(nbits):
        if tbits[b] == 0:
            qc.x(sum_anc[b])

    for i in range(n - 1, -1, -1):
        add_constant_inv(a[i], problem_qubits[i])
