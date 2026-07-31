import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [4, 5, 5]
    T = 9
    n = len(a)
    maxsum = sum(a)
    nbits = max(1, math.ceil(math.log2(maxsum + 1)))
    sum_reg = ancilla_qubits[:nbits]
    flag = ancilla_qubits[nbits]

    def controlled_increment(ctrl):
        for i in range(nbits - 1, 0, -1):
            controls = [ctrl] + sum_reg[:i]
            qc.mcx(controls, sum_reg[i])
        qc.cx(ctrl, sum_reg[0])

    def controlled_decrement(ctrl):
        qc.cx(ctrl, sum_reg[0])
        for i in range(1, nbits):
            controls = [ctrl] + sum_reg[:i]
            qc.mcx(controls, sum_reg[i])

    # compute: sum_reg += a[i] if selected
    for i in range(n):
        for _ in range(a[i]):
            controlled_increment(problem_qubits[i])

    # phase: -1 iff sum_reg == T
    Tbits = [(T >> k) & 1 for k in range(nbits)]
    for k in range(nbits):
        if Tbits[k] == 0:
            qc.x(sum_reg[k])
    qc.h(flag)
    qc.x(flag)
    qc.mcx(sum_reg, flag)
    qc.x(flag)
    qc.h(flag)
    for k in range(nbits):
        if Tbits[k] == 0:
            qc.x(sum_reg[k])

    # uncompute
    for i in range(n - 1, -1, -1):
        for _ in range(a[i]):
            controlled_decrement(problem_qubits[i])
