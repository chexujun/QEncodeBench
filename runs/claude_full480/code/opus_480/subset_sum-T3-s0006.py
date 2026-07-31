from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [3, 4, 5, 14, 13]
    T = 21
    nbits = 5  # sum max = 3+4+5+14+13 = 39 < 64, but 5 bits enough? 39 -> 6 bits. use 5? need 6

    # sum ranges 0..39 -> need 6 bits. ancillas: 6 available, need them all for the adder register.
    # We build a running-sum register in ancilla_qubits[0..5] (6 qubits), LSB first.
    nbits = 6
    reg = ancilla_qubits[0:6]

    def add_constant(const, ctrl):
        # controlled (by ctrl) add of classical constant `const` into reg (mod 2^nbits),
        # implemented as a sequence of controlled increments using ripple via MCX.
        # Add const if ctrl==1. We add bit-by-bit with carry using controlled adder of a constant.
        # Use standard controlled constant addition via cascaded MCX on the register.
        bits = [(const >> k) & 1 for k in range(nbits)]
        for k in range(nbits):
            if bits[k] == 0:
                continue
            # add 1 at position k: this means increment reg starting at bit k.
            # increment: for position j from top down to k: flip reg[j] if all lower (k..j-1) are 1 AND ctrl
            for j in range(nbits - 1, k, -1):
                controls = [ctrl] + reg[k:j]
                qc.mcx(controls, reg[j])
            qc.cx(ctrl, reg[k])

    # compute running sum
    for i in range(5):
        add_constant(a[i], problem_qubits[i])

    # phase: -1 iff reg == T
    Tbits = [(T >> k) & 1 for k in range(nbits)]
    for k in range(nbits):
        if Tbits[k] == 0:
            qc.x(reg[k])
    qc.h(reg[nbits - 1])
    qc.mcx(reg[0:nbits - 1], reg[nbits - 1])
    qc.h(reg[nbits - 1])
    for k in range(nbits):
        if Tbits[k] == 0:
            qc.x(reg[k])

    # uncompute running sum (reverse)
    def add_constant_inv(const, ctrl):
        bits = [(const >> k) & 1 for k in range(nbits)]
        for k in reversed(range(nbits)):
            if bits[k] == 0:
                continue
            qc.cx(ctrl, reg[k])
            for j in range(k + 1, nbits):
                controls = [ctrl] + reg[k:j]
                qc.mcx(controls, reg[j])

    for i in reversed(range(5)):
        add_constant_inv(a[i], problem_qubits[i])
