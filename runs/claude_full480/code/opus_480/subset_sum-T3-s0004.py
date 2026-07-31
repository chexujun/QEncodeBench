from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [11, 6, 5, 11, 6]
    T = 22
    n = len(a)
    total = sum(a)
    nbits = total.bit_length()  # bits needed to hold sums up to 39 -> 6 bits

    s = ancilla_qubits[:nbits]  # sum register (6 ancillas)

    def add_constant(const, control):
        # controlled increment of sum register s by integer `const`, controlled on `control`
        # ripple: for each bit position, add const bits with carry, all controlled on `control`.
        # Implement as controlled addition of a classical constant into register s.
        for _ in range(1):
            pass
        # Use schoolbook: add const to s (mod 2^nbits) controlled on `control`.
        # We add bit by bit from LSB, propagating carry using ancilla-free technique:
        # controlled add of constant = sequence of controlled increments weighted.
        # Simpler: represent const in binary and add via repeated controlled-add-power-of-two.
        # We implement a controlled ripple adder of a constant using MCX gates.
        bits = [(const >> k) & 1 for k in range(nbits)]
        # Add constant to register conditioned on control using reversible ripple:
        # process from MSB down for carry-free constant addition trick.
        for i in reversed(range(nbits)):
            # if adding a 1 at position i (from constant), toggle with carry chain
            if bits[i]:
                for j in reversed(range(i + 1, nbits)):
                    # carry: bit j flips if all lower bits from i..j-1 are 1 and control set
                    ctrls = [control] + [s[k] for k in range(i, j)]
                    qc.mcx(ctrls, s[j])
                qc.cx(control, s[i])

    # compute sum of selected elements into s
    for i in range(n):
        add_constant(a[i], problem_qubits[i])

    # phase: mark when s == T
    Tbits = [(T >> k) & 1 for k in range(nbits)]
    for k in range(nbits):
        if not Tbits[k]:
            qc.x(s[k])
    qc.h(s[nbits - 1])
    qc.mcx(s[:nbits - 1], s[nbits - 1])
    qc.h(s[nbits - 1])
    for k in range(nbits):
        if not Tbits[k]:
            qc.x(s[k])

    # uncompute sum
    def add_constant_inv(const, control):
        bits = [(const >> k) & 1 for k in range(nbits)]
        for i in range(nbits):
            if bits[i]:
                qc.cx(control, s[i])
                for j in range(i + 1, nbits):
                    ctrls = [control] + [s[k] for k in range(i, j)]
                    qc.mcx(ctrls, s[j])

    for i in reversed(range(n)):
        add_constant_inv(a[i], problem_qubits[i])
