import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [2, 5, 4]
    T = 4
    # sum bits needed: max sum = 11 -> 4 bits
    s = ancilla_qubits[0:4]  # sum register (little-endian), 4 qubits

    def add_constant(const):
        # add classical constant `const` into sum register s (mod 2^4), no carry-out beyond register
        for bit_pos in range(4):
            if (const >> bit_pos) & 1:
                # add 1 at position bit_pos: ripple carry using the register itself
                for j in range(3, bit_pos, -1):
                    ctrls = s[bit_pos:j]
                    qc.mcx(ctrls, s[j])
                qc.x(s[bit_pos])

    def add_constant_inv(const):
        for bit_pos in range(4):
            if (const >> bit_pos) & 1:
                qc.x(s[bit_pos])
                for j in range(bit_pos + 1, 4):
                    ctrls = s[bit_pos:j]
                    qc.mcx(ctrls, s[j])

    def cadd_constant(ctrl, const):
        for bit_pos in range(4):
            if (const >> bit_pos) & 1:
                for j in range(3, bit_pos, -1):
                    ctrls = [ctrl] + s[bit_pos:j]
                    qc.mcx(ctrls, s[j])
                qc.cx(ctrl, s[bit_pos])

    def cadd_constant_inv(ctrl, const):
        for bit_pos in range(4):
            if (const >> bit_pos) & 1:
                qc.cx(ctrl, s[bit_pos])
                for j in range(bit_pos + 1, 4):
                    ctrls = [ctrl] + s[bit_pos:j]
                    qc.mcx(ctrls, s[j])

    # compute: sum = sum of selected a[i]
    for i in range(3):
        cadd_constant(problem_qubits[i], a[i])

    # phase: -1 iff sum register == T (4 bits)
    for bit_pos in range(4):
        if not ((T >> bit_pos) & 1):
            qc.x(s[bit_pos])
    qc.h(s[3])
    qc.mcx(s[0:3], s[3])
    qc.h(s[3])
    for bit_pos in range(4):
        if not ((T >> bit_pos) & 1):
            qc.x(s[bit_pos])

    # uncompute
    for i in range(2, -1, -1):
        cadd_constant_inv(problem_qubits[i], a[i])
