import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    a = [5, 9, 9, 10]
    T = 24
    n = len(a)
    maxsum = sum(a)
    nbits = maxsum.bit_length()

    s = ancilla_qubits[:nbits]
    flag = ancilla_qubits[nbits]

    def add_constant_controlled(ctrl, const):
        for bit in range(nbits - 1, -1, -1):
            if (const >> bit) & 1:
                for j in range(nbits - 1, bit, -1):
                    controls = [ctrl] + s[bit:j]
                    qc.mcx(controls, s[j])
                qc.cx(ctrl, s[bit])

    def add_constant_controlled_inv(ctrl, const):
        for bit in range(0, nbits):
            if (const >> bit) & 1:
                qc.cx(ctrl, s[bit])
                for j in range(bit + 1, nbits):
                    controls = [ctrl] + s[bit:j]
                    qc.mcx(controls, s[j])

    for i in range(n):
        add_constant_controlled(problem_qubits[i], a[i])

    for bit in range(nbits):
        if not ((T >> bit) & 1):
            qc.x(s[bit])

    qc.mcx(s, flag)
    qc.z(flag)
    qc.mcx(s, flag)

    for bit in range(nbits):
        if not ((T >> bit) & 1):
            qc.x(s[bit])

    for i in range(n - 1, -1, -1):
        add_constant_controlled_inv(problem_qubits[i], a[i])
