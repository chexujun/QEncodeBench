from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [3, 1, 6]
    T = 3
    nbits = max(1, T.bit_length())  # bits needed to hold sums up to T; overflow handled by extra ancilla

    # ancilla layout: use ancilla_qubits as an accumulator register plus one flag
    # We accumulate sum(selected a[i]) into an ancilla register conditioned on problem qubits,
    # then check equality with T, phase, then uncompute.
    #
    # Sum range: 0..10 -> needs 4 bits. We have 4 ancillas. Use all 4 as the sum register,
    # and realize the phase directly via a multi-controlled phase on the register matching T.
    reg = list(ancilla_qubits[:4])  # 4-bit accumulator, LSB first
    n = len(reg)

    def add_constant_controlled(ctrl, c):
        # Add classical constant c into reg (LSB-first) controlled on qubit ctrl.
        # Ripple add of a constant: process bits; for each set bit of c we add,
        # with carries realized via multi-controlled X. Controlled overall by ctrl.
        for i in range(n):
            # add value (c) starting at bit position i using standard schoolbook:
            pass

    # Simpler robust approach: controlled ripple-carry increment by constant.
    def add_const(ctrl, c):
        cbits = [(c >> k) & 1 for k in range(n)]
        # Add cbits (a constant) into reg controlled on ctrl, LSB to MSB with carry propagation.
        # Implement by, for each bit where cbits is 1, performing a controlled increment
        # starting at that position.
        for start in range(n):
            if cbits[start] == 0:
                continue
            # increment reg from position `start` by 1, controlled on ctrl:
            # carry chain: flip higher bits controlled on all lower ones being 1 (and ctrl).
            for j in range(n - 1, start, -1):
                controls = [ctrl] + reg[start:j]
                qc.mcx(controls, reg[j])
            qc.cx(ctrl, reg[start])

    # Compute the sum of selected elements into reg.
    for i in range(3):
        add_const(problem_qubits[i], a[i])

    # Phase -1 iff reg == T. mcp with pi on the pattern of T.
    Tbits = [(T >> k) & 1 for k in range(n)]
    for k in range(n):
        if Tbits[k] == 0:
            qc.x(reg[k])
    qc.h(reg[n - 1])
    qc.mcx(reg[:n - 1], reg[n - 1])
    qc.h(reg[n - 1])
    for k in range(n):
        if Tbits[k] == 0:
            qc.x(reg[k])

    # Uncompute the sum (mirror).
    def add_const_inv(ctrl, c):
        cbits = [(c >> k) & 1 for k in range(n)]
        for start in reversed(range(n)):
            if cbits[start] == 0:
                continue
            qc.cx(ctrl, reg[start])
            for j in range(start + 1, n):
                controls = [ctrl] + reg[start:j]
                qc.mcx(controls, reg[j])

    for i in reversed(range(3)):
        add_const_inv(problem_qubits[i], a[i])
