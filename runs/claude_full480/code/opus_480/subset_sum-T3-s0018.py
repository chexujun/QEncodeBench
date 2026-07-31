import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [15, 11, 9, 13, 7]
    T = 40
    n = len(a)
    maxsum = sum(a)
    W = maxsum.bit_length()  # bits needed for sum register

    s = ancilla_qubits[:W]          # sum register (little-endian)
    flag = ancilla_qubits[W]        # predicate flag

    def add_constant(control, c):
        # Controlled addition of constant c into register s (in-place, ripple via
        # controlled increments). Implemented as: for each set bit contribution,
        # add using a controlled ripple. Simpler: add c by controlled increment c times
        # is too deep; instead do controlled binary addition of constant.
        # We add constant c into s, controlled on `control`.
        cbits = [(c >> j) & 1 for j in range(W)]
        # Ripple-carry add of constant. Process from MSB to LSB using the standard
        # "add constant" pattern with controlled multi-controlled X gates.
        for i in range(W - 1, -1, -1):
            if cbits[i] == 0:
                continue
            # adding 1 at position i: flip s[i], with carries into higher bits
            for j in range(W - 1, i, -1):
                # carry out of bit j happens if all bits i..j-1 are 1 (and control)
                ctrls = [control] + [s[k] for k in range(i, j)]
                qc.mcx(ctrls, s[j])
            qc.cx(control, s[i])

    def add_constant_inv(control, c):
        cbits = [(c >> j) & 1 for j in range(W)]
        for i in range(0, W):
            if cbits[i] == 0:
                continue
            qc.cx(control, s[i])
            for j in range(i + 1, W):
                ctrls = [control] + [s[k] for k in range(i, j)]
                qc.mcx(ctrls, s[j])

    # compute: s = sum of selected elements
    for i in range(n):
        add_constant(problem_qubits[i], a[i])

    # phase: mark states where s == T
    Tbits = [(T >> j) & 1 for j in range(W)]
    for j in range(W):
        if Tbits[j] == 0:
            qc.x(s[j])
    qc.h(flag)
    qc.mcx(s, flag)
    qc.h(flag)
    for j in range(W):
        if Tbits[j] == 0:
            qc.x(s[j])

    # uncompute: reverse the summation
    for i in range(n - 1, -1, -1):
        add_constant_inv(problem_qubits[i], a[i])
