from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [5, 6, 3]
    T = 6
    n = len(a)
    nbits = max(1, int(np.ceil(np.log2(sum(a) + 1))))
    sum_anc = ancilla_qubits[:nbits]
    flag = ancilla_qubits[nbits]

    def add_constant_controlled(ctrl, const):
        # add `const` into the sum register (little-endian) conditioned on ctrl,
        # using ripple carry via successive controlled increments.
        for _ in range(const):
            increment_controlled(ctrl)

    def increment_controlled(ctrl):
        # controlled +1 on sum register: ripple of MCX with decreasing controls
        for i in range(nbits - 1, 0, -1):
            controls = [ctrl] + sum_anc[:i]
            qc.mcx(controls, sum_anc[i])
        qc.cx(ctrl, sum_anc[0])

    def compute():
        for i in range(n):
            add_constant_controlled(problem_qubits[i], a[i])

    def uncompute():
        for i in reversed(range(n)):
            for _ in range(a[i]):
                # inverse increment: reverse order of increment
                qc.cx(problem_qubits[i], sum_anc[0])
                for k in range(1, nbits):
                    controls = [problem_qubits[i]] + sum_anc[:k]
                    qc.mcx(controls, sum_anc[k])

    compute()

    # phase -1 iff sum register == T
    Tbits = [(T >> k) & 1 for k in range(nbits)]
    for k in range(nbits):
        if Tbits[k] == 0:
            qc.x(sum_anc[k])
    qc.h(flag)
    qc.mcx(sum_anc, flag)
    qc.h(flag)
    for k in range(nbits):
        if Tbits[k] == 0:
            qc.x(sum_anc[k])

    uncompute()
