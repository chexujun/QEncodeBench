from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [13, 10, 5, 14, 3]
    T = 37
    n = len(a)
    # 6-bit sum register on ancillas (max sum = 45 < 64)
    s = ancilla_qubits[0:6]

    def add_const(val):
        # ripple-add classical constant `val` into the 6-qubit register s,
        # controlled by an implicit selection handled outside via controlled gates.
        pass

    # We add each selected a[i] into the register s conditioned on problem_qubits[i].
    # Adder: for a constant c controlled by qubit ctrl, add c into s (6 bits).
    def cadd_const(ctrl, c):
        # add constant c into register s (LSB = s[0]) controlled by ctrl,
        # ripple from MSB down to avoid clobbering: use standard controlled
        # increment-by-constant via bit decomposition with carry through MCX.
        bits = [(c >> k) & 1 for k in range(6)]
        # Process from most significant to least significant bit position.
        for j in range(5, -1, -1):
            if bits[j] == 0:
                continue
            # add 1 at position j: this may ripple carries upward through s[j..5].
            for k in range(5, j, -1):
                ctrls = [ctrl] + s[j:k]
                qc.mcx(ctrls, s[k])
            qc.cx(ctrl, s[j])

    # compute sum
    for i in range(n):
        cadd_const(problem_qubits[i], a[i])

    # phase: mark states where s == T (37 = 0b100101)
    Tbits = [(T >> k) & 1 for k in range(6)]
    for k in range(6):
        if Tbits[k] == 0:
            qc.x(s[k])
    # multi-controlled Z on all 6 register qubits
    qc.h(s[5])
    qc.mcx(s[0:5], s[5])
    qc.h(s[5])
    for k in range(6):
        if Tbits[k] == 0:
            qc.x(s[k])

    # uncompute sum (reverse order, reverse each adder)
    def cadd_const_inv(ctrl, c):
        bits = [(c >> k) & 1 for k in range(6)]
        for j in range(0, 6):
            if bits[j] == 0:
                continue
            qc.cx(ctrl, s[j])
            for k in range(j + 1, 6):
                ctrls = [ctrl] + s[j:k]
                qc.mcx(ctrls, s[k])

    for i in range(n - 1, -1, -1):
        cadd_const_inv(problem_qubits[i], a[i])
