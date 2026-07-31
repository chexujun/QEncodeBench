import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [4, 9, 1, 9]
    T = 9
    n = len(a)
    maxsum = sum(a)
    W = maxsum.bit_length()  # number of sum-register bits

    sum_reg = ancilla_qubits[:W]
    flag = ancilla_qubits[W]

    def add_constant_controlled(ctrl, c):
        # Add constant c into sum_reg (LSB first), controlled on ctrl.
        # Ripple using the fact that adding a constant = sequence of
        # controlled increments per set bit, with carry propagation via mcx.
        for _ in range(c):
            _increment_controlled(ctrl)

    def _increment_controlled(ctrl):
        # Controlled +1 on sum_reg, ripple-carry, MSB-first flips.
        for i in range(W - 1, 0, -1):
            controls = [ctrl] + sum_reg[:i]
            qc.mcx(controls, sum_reg[i])
        qc.cx(ctrl, sum_reg[0])

    def _decrement_controlled(ctrl):
        # Inverse of increment.
        qc.cx(ctrl, sum_reg[0])
        for i in range(1, W):
            controls = [ctrl] + sum_reg[:i]
            qc.mcx(controls, sum_reg[i])

    def sub_constant_controlled(ctrl, c):
        for _ in range(c):
            _decrement_controlled(ctrl)

    # Compute: accumulate selected values into sum_reg
    for i in range(n):
        add_constant_controlled(problem_qubits[i], a[i])

    # Phase: -1 iff sum_reg == T
    Tbits = [(T >> k) & 1 for k in range(W)]
    for k in range(W):
        if Tbits[k] == 0:
            qc.x(sum_reg[k])
    qc.h(flag)
    qc.x(flag)
    qc.mcx(sum_reg, flag)
    qc.x(flag)
    qc.h(flag)
    for k in range(W):
        if Tbits[k] == 0:
            qc.x(sum_reg[k])

    # Uncompute: mirror the accumulation
    for i in range(n - 1, -1, -1):
        sub_constant_controlled(problem_qubits[i], a[i])
