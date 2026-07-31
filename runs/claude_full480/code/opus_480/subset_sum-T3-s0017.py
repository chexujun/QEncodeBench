from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [15, 5, 10, 4, 2]
    T = 10
    n = len(a)
    # Sum ranges 0..36, needs 6 bits. Use 6 ancillas as a running sum register.
    s = ancilla_qubits[:6]
    m = len(s)

    def add_constant(ctrl, c):
        # Controlled add of constant c (mod 2^m) into register s (LSB = s[0]),
        # using ctrl as the control. Implemented via controlled ripple using
        # incrementer decomposition: add c by adding each set bit with carry.
        # We implement controlled addition by the standard "controlled increment
        # by constant" using a sequence of multi-controlled X gates (carry chain).
        for j in range(m - 1, -1, -1):
            if (c >> j) & 1:
                # add 1 at position j: flip s[j], carry into higher bits
                for k in range(m - 1, j, -1):
                    controls = [ctrl] + [s[t] for t in range(j, k)]
                    qc.mcx(controls, s[k])
                qc.cx(ctrl, s[j])

    # compute: sum of selected a[i] into register s
    for i in range(n):
        add_constant(problem_qubits[i], a[i])

    # phase: -1 iff s == T
    Tbits = [(T >> j) & 1 for j in range(m)]
    for j in range(m):
        if Tbits[j] == 0:
            qc.x(s[j])
    qc.h(s[m - 1])
    qc.mcx(s[:m - 1], s[m - 1])
    qc.h(s[m - 1])
    for j in range(m):
        if Tbits[j] == 0:
            qc.x(s[j])

    # uncompute: reverse of compute
    for i in range(n - 1, -1, -1):
        ctrl = problem_qubits[i]
        c = a[i]
        for j in range(0, m):
            if (c >> j) & 1:
                qc.cx(ctrl, s[j])
                for k in range(j + 1, m):
                    controls = [ctrl] + [s[t] for t in range(j, k)]
                    qc.mcx(controls, s[k])
