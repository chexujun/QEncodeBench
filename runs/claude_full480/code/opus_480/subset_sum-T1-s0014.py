from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = problem_qubits
    values = [6, 5, 3]
    T = 5
    nbits = 3  # sum ranges 0..14, needs 4 bits, but we track via adder ancillas

    # Ancillas: use 4 ancillas as a running-sum register (values <= 14 -> 4 bits)
    s = ancilla_qubits[:4]  # sum register bits s[0] (LSB) .. s[3] (MSB)

    def add_constant_controlled(ctrl, c):
        # add integer c into register s, controlled on qubit ctrl.
        # ripple using the fact c is a known constant; do controlled increments.
        # Implement as controlled add of constant via bit-by-bit with carry using MCX.
        for _ in range(c):
            # controlled increment of register s by 1, controlled on ctrl
            # increment: ripple carry. bit0 flips; carry propagates.
            # s[3] ^= ctrl & s[2] & s[1] & s[0]
            qc.mcx([ctrl, s[0], s[1], s[2]], s[3])
            qc.mcx([ctrl, s[0], s[1]], s[2])
            qc.mcx([ctrl, s[0]], s[1])
            qc.cx(ctrl, s[0])

    def uncompute_add_constant_controlled(ctrl, c):
        for _ in range(c):
            qc.cx(ctrl, s[0])
            qc.mcx([ctrl, s[0]], s[1])
            qc.mcx([ctrl, s[0], s[1]], s[2])
            qc.mcx([ctrl, s[0], s[1], s[2]], s[3])

    # compute sum into s
    for i in range(3):
        add_constant_controlled(a[i], values[i])

    # phase -1 iff s == T (binary of 5 = 0101 -> s0=1,s1=0,s2=1,s3=0)
    Tbits = [(T >> k) & 1 for k in range(4)]
    for k in range(4):
        if Tbits[k] == 0:
            qc.x(s[k])
    qc.h(s[3])
    qc.mcx([s[0], s[1], s[2]], s[3])
    qc.h(s[3])
    for k in range(4):
        if Tbits[k] == 0:
            qc.x(s[k])

    # uncompute sum
    for i in reversed(range(3)):
        uncompute_add_constant_controlled(a[i], values[i])
