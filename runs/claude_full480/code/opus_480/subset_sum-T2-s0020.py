from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [9, 9, 9, 7]
    T = 27
    n = len(a)
    maxsum = sum(a)
    nbits = maxsum.bit_length()

    sum_q = ancilla_qubits[:nbits]
    flag = ancilla_qubits[nbits]

    def add_constant(const, control):
        for _ in range(1):
            pass
        c = const
        for j in range(nbits):
            step = []
            for k in range(nbits - 1, j - 1, -1):
                controls = [control] + sum_q[j:k]
                qc.mcx(controls, sum_q[k])
        return

    def add_const_controlled(const, control):
        bits = [(const >> i) & 1 for i in range(nbits)]
        for j in range(nbits - 1, -1, -1):
            if bits[j]:
                for k in range(nbits - 1, j - 1, -1):
                    ctrls = [control] + sum_q[j:k]
                    qc.mcx(ctrls, sum_q[k])

    for i in range(n):
        add_const_controlled(a[i], problem_qubits[i])

    tbits = [(T >> i) & 1 for i in range(nbits)]
    for j in range(nbits):
        if tbits[j] == 0:
            qc.x(sum_q[j])

    qc.mcx(sum_q, flag)
    qc.z(flag)
    qc.mcx(sum_q, flag)

    for j in range(nbits):
        if tbits[j] == 0:
            qc.x(sum_q[j])

    for i in range(n - 1, -1, -1):
        const = a[i]
        control = problem_qubits[i]
        bits = [(const >> k) & 1 for k in range(nbits)]
        for j in range(nbits):
            if bits[j]:
                for k in range(j, nbits):
                    ctrls = [control] + sum_q[j:k]
                    qc.mcx(ctrls, sum_q[k])
