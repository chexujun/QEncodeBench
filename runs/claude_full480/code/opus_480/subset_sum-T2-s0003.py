from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [9, 3, 8, 9]
    T = 9
    n = len(a)

    # Number of bits needed to hold the running sum (max sum = 29 -> 5 bits)
    maxsum = sum(a)
    W = maxsum.bit_length()  # 5

    sum_bits = ancilla_qubits[:W]      # register holding the running sum
    flag = ancilla_qubits[W]           # phase flag ancilla

    def add_constant(const, ctrl):
        # Controlled add of `const` into the sum register (little-endian),
        # controlled on qubit `ctrl`. Ripple using MCX with increasing controls.
        for bit in range(W - 1, -1, -1):
            if (const >> bit) & 1:
                # add 1 at position `bit`: propagate carries from top down
                for j in range(W - 1, bit, -1):
                    controls = [ctrl] + sum_bits[bit:j]
                    qc.mcx(controls, sum_bits[j])
                qc.cx(ctrl, sum_bits[bit])

    def add_constant_inv(const, ctrl):
        for bit in range(W):
            if (const >> bit) & 1:
                qc.cx(ctrl, sum_bits[bit])
                for j in range(bit + 1, W):
                    controls = [ctrl] + sum_bits[bit:j]
                    qc.mcx(controls, sum_bits[j])

    # Compute running sum = sum of selected a[i]
    for i in range(n):
        add_constant(a[i], problem_qubits[i])

    # Phase -1 iff sum register == T
    Tbits = [(T >> b) & 1 for b in range(W)]
    for b in range(W):
        if Tbits[b] == 0:
            qc.x(sum_bits[b])
    qc.h(flag)
    qc.mcx(sum_bits, flag)
    qc.h(flag)
    for b in range(W):
        if Tbits[b] == 0:
            qc.x(sum_bits[b])

    # Uncompute running sum
    for i in range(n - 1, -1, -1):
        add_constant_inv(a[i], problem_qubits[i])
