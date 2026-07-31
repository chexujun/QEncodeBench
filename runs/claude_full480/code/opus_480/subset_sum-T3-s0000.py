import numpy as np
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    a = [7, 10, 5, 3, 9]
    T = 16
    n = len(a)
    # sum register width: sum max = 34 -> needs 6 bits
    W = 6
    s = ancilla_qubits[:W]  # sum register, initialized |0>

    def add_constant_controlled(ctrl, const):
        # add `const` into register s (little-endian) controlled on ctrl,
        # using ripple via controlled increments implemented with mcx cascades
        for i in range(W):
            if (const >> i) & 1:
                # add 1 at position i (controlled by ctrl): ripple carry
                for j in range(W - 1, i, -1):
                    controls = [ctrl] + s[i:j]
                    qc.mcx(controls, s[j])
                qc.cx(ctrl, s[i])

    def add_constant_controlled_inv(ctrl, const):
        for i in range(W):
            if (const >> i) & 1:
                qc.cx(ctrl, s[i])
                for j in range(i + 1, W):
                    controls = [ctrl] + s[i:j]
                    qc.mcx(controls, s[j])

    # compute sum
    for k in range(n):
        add_constant_controlled(problem_qubits[k], a[k])

    # phase -1 iff s == T (little-endian bits of T)
    tbits = [(T >> i) & 1 for i in range(W)]
    for i in range(W):
        if tbits[i] == 0:
            qc.x(s[i])
    # multi-controlled Z on all W sum qubits
    qc.h(s[W - 1])
    qc.mcx(s[:W - 1], s[W - 1])
    qc.h(s[W - 1])
    for i in range(W):
        if tbits[i] == 0:
            qc.x(s[i])

    # uncompute sum
    for k in range(n - 1, -1, -1):
        add_constant_controlled_inv(problem_qubits[k], a[k])
