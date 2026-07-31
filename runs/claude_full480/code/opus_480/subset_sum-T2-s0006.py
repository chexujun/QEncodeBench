from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [1, 7, 2, 4]
    T = 1
    n = len(a)
    maxsum = sum(a)
    width = maxsum.bit_length()

    sum_anc = ancilla_qubits[:width]
    flag = ancilla_qubits[width]

    def add_constant(const, controls):
        for k in range(width - 1, -1, -1):
            for j in range(width - 1, k - 1, -1):
                block = (const >> (j - k)) & ((1 << (width - j)) - 1)
            # placeholder to keep structure; real add below
            pass

    def ripple_add_const(const, ctrl):
        for target in range(width - 1, -1, -1):
            if (const >> target) & 1:
                ctrls = [ctrl] + sum_anc[:target]
                if len(ctrls) == 0:
                    qc.x(sum_anc[target])
                else:
                    qc.mcx(ctrls, sum_anc[target])

    for i in range(n):
        ripple_add_const(a[i], problem_qubits[i])

    tbits = [(T >> k) & 1 for k in range(width)]
    for k in range(width):
        if tbits[k] == 0:
            qc.x(sum_anc[k])
    qc.h(flag)
    qc.mcx(sum_anc, flag)
    qc.h(flag)
    for k in range(width):
        if tbits[k] == 0:
            qc.x(sum_anc[k])

    for i in range(n - 1, -1, -1):
        for target in range(width):
            if (a[i] >> target) & 1:
                ctrls = [problem_qubits[i]] + sum_anc[:target]
                if len(ctrls) == 0:
                    qc.x(sum_anc[target])
                else:
                    qc.mcx(ctrls, sum_anc[target])
