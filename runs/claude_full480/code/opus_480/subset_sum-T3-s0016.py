from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [9, 12, 2, 9, 15]
    T = 26
    n = len(problem_qubits)

    # 6 ancilla qubits hold the running sum (max sum = 47 -> needs 6 bits: 0..63)
    s = ancilla_qubits[:6]
    nbits = len(s)

    def add_constant_controlled(ctrl, c):
        # Add constant c into the sum register s, controlled on qubit ctrl.
        # Ripple: for each bit position from MSB down, use controlled increments.
        # Implement via controlled ripple-carry using the standard "add classical
        # constant" trick: increment register by c when ctrl=1.
        # We realize controlled addition of constant using a sequence of
        # controlled multi-controlled-X gates (increment approach) repeated,
        # but that is expensive; instead use bitwise carry addition.
        pass

    # Controlled adder of a classical constant into register s, control = ctrl.
    # We use the "increment by constant" via carry-ripple built from MCX gates.
    def cadd(ctrl, c):
        # Add classical constant c (>=0) to little-endian register s, controlled.
        # Process each set bit of c as a controlled addition of a power of two,
        # implemented as a controlled increment at that bit position with ripple.
        for bitpos in range(nbits):
            if (c >> bitpos) & 1:
                # controlled increment of subregister s[bitpos:] by 1
                # ripple carry: flip highest bits first using MCX with controls
                for j in range(nbits - 1, bitpos, -1):
                    controls = [ctrl] + s[bitpos:j]
                    qc.mcx(controls, s[j])
                qc.cx(ctrl, s[bitpos])

    def cadd_inv(ctrl, c):
        for bitpos in range(nbits):
            if (c >> bitpos) & 1:
                qc.cx(ctrl, s[bitpos])
                for j in range(bitpos + 1, nbits):
                    controls = [ctrl] + s[bitpos:j]
                    qc.mcx(controls, s[j])

    # Compute: sum selected elements into s
    for i in range(n):
        cadd(problem_qubits[i], a[i])

    # Phase: -1 iff s == T (little-endian bits)
    zero_bits = [b for b in range(nbits) if not ((T >> b) & 1)]
    for b in zero_bits:
        qc.x(s[b])
    qc.h(s[nbits - 1])
    qc.mcx(s[:nbits - 1], s[nbits - 1])
    qc.h(s[nbits - 1])
    for b in zero_bits:
        qc.x(s[b])

    # Uncompute: reverse the additions
    for i in reversed(range(n)):
        cadd_inv(problem_qubits[i], a[i])
