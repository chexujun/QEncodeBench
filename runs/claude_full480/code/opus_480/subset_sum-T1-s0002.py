import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [6, 5, 6]
    T = 6
    n = len(a)
    W = max(T, sum(a)) + 1
    nbits = max(1, math.ceil(math.log2(W + 1)))
    sum_reg = ancilla_qubits[:nbits]
    flag = ancilla_qubits[nbits]

    def add_constant(ctrl, c):
        # controlled add of constant c into sum_reg (little-endian ripple, LSB-first)
        # use controlled increment-by-constant via a sequence of controlled adds
        # implement addition of constant c to sum_reg conditioned on ctrl
        bits = [(c >> k) & 1 for k in range(nbits)]
        # ripple-carry add of constant using MSB-to-LSB controlled increments
        for k in range(nbits - 1, -1, -1):
            if bits[k]:
                # add 2^k to sum_reg controlled on ctrl -> increment starting at bit k
                for j in range(nbits - 1, k, -1):
                    controls = [ctrl] + sum_reg[k:j]
                    qc.mcx(controls, sum_reg[j])
                qc.cx(ctrl, sum_reg[k])

    def sub_constant(ctrl, c):
        bits = [(c >> k) & 1 for k in range(nbits)]
        for k in range(nbits):
            if bits[k]:
                qc.cx(ctrl, sum_reg[k])
                for j in range(k + 1, nbits):
                    controls = [ctrl] + sum_reg[k:j]
                    qc.mcx(controls, sum_reg[j])

    # compute: sum_reg = sum of selected a[i]
    for i in range(n):
        add_constant(problem_qubits[i], a[i])

    # flag = 1 iff sum_reg == T
    tbits = [(T >> k) & 1 for k in range(nbits)]
    for k in range(nbits):
        if tbits[k] == 0:
            qc.x(sum_reg[k])
    qc.mcx(sum_reg, flag)
    for k in range(nbits):
        if tbits[k] == 0:
            qc.x(sum_reg[k])

    # phase
    qc.z(flag)

    # uncompute flag
    for k in range(nbits):
        if tbits[k] == 0:
            qc.x(sum_reg[k])
    qc.mcx(sum_reg, flag)
    for k in range(nbits):
        if tbits[k] == 0:
            qc.x(sum_reg[k])

    # uncompute sum_reg
    for i in range(n - 1, -1, -1):
        sub_constant(problem_qubits[i], a[i])
