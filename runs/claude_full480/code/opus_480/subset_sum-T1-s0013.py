from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [5, 2, 3]
    T = 5
    n = len(a)
    # sum range 0..10 -> need 4 sum bits; use ancilla_qubits[0:4] as sum register
    s = ancilla_qubits[0:4]
    nbits = 4

    def add_constant(ctrl, c):
        # controlled (on ctrl) addition of constant c into register s (little-endian), modular but range-safe
        for k in range(nbits - 1, -1, -1):
            bit = (c >> k) & 1
            if bit:
                # add 1 at position k with carry propagation, all controlled by ctrl
                for j in range(nbits - 1, k, -1):
                    ctrls = [ctrl] + s[k:j]
                    qc.mcx(ctrls, s[j])
                qc.cx(ctrl, s[k])

    # compute sum of selected elements into s
    for i in range(n):
        add_constant(problem_qubits[i], a[i])

    # phase -1 iff s == T (little-endian)
    tbits = [(T >> k) & 1 for k in range(nbits)]
    for k in range(nbits):
        if tbits[k] == 0:
            qc.x(s[k])
    qc.h(s[nbits - 1])
    qc.mcx(s[0:nbits - 1], s[nbits - 1])
    qc.h(s[nbits - 1])
    for k in range(nbits):
        if tbits[k] == 0:
            qc.x(s[k])

    # uncompute sum (reverse order, addition is its own structured inverse when reversed)
    def add_constant_inv(ctrl, c):
        for k in range(0, nbits):
            bit = (c >> k) & 1
            if bit:
                qc.cx(ctrl, s[k])
                for j in range(k + 1, nbits):
                    ctrls = [ctrl] + s[k:j]
                    qc.mcx(ctrls, s[j])

    for i in range(n - 1, -1, -1):
        add_constant_inv(problem_qubits[i], a[i])
