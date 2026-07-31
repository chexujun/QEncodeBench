from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [12, 13, 14, 13, 6]
    T = 12
    n = len(a)
    # Sum range: max sum = 12+13+14+13+6 = 58, needs 6 bits (0..63)
    # Use 6 ancilla qubits as a binary accumulator for the running sum.
    acc = ancilla_qubits[:6]
    W = len(acc)

    def add_constant_controlled(ctrl, c):
        # Add constant c into the accumulator register acc (LSB = acc[0]),
        # conditioned on control qubit ctrl. Ripple increment using MCX.
        bits = [(c >> j) & 1 for j in range(W)]
        for j in range(W):
            if bits[j] == 1:
                # Add 1 at position j: acc[j] ^= 1, with carry to higher bits.
                # Carry chain: from top down, flip acc[k] if all lower target bits (>=j) are 1.
                for k in range(W - 1, j, -1):
                    controls = [ctrl] + [acc[m] for m in range(j, k)]
                    qc.mcx(controls, acc[k])
                qc.cx(ctrl, acc[j])

    def add_constant_controlled_inv(ctrl, c):
        bits = [(c >> j) & 1 for j in range(W)]
        for j in range(W - 1, -1, -1):
            if bits[j] == 1:
                qc.cx(ctrl, acc[j])
                for k in range(j + 1, W):
                    controls = [ctrl] + [acc[m] for m in range(j, k)]
                    qc.mcx(controls, acc[k])

    # Compute the running sum into acc.
    for i in range(n):
        add_constant_controlled(problem_qubits[i], a[i])

    # Phase: -1 iff acc == T (binary of 12 over W bits).
    tbits = [(T >> j) & 1 for j in range(W)]
    for j in range(W):
        if tbits[j] == 0:
            qc.x(acc[j])
    qc.h(acc[W - 1])
    qc.mcx(acc[:W - 1], acc[W - 1])
    qc.h(acc[W - 1])
    for j in range(W):
        if tbits[j] == 0:
            qc.x(acc[j])

    # Uncompute the running sum.
    for i in range(n - 1, -1, -1):
        add_constant_controlled_inv(problem_qubits[i], a[i])
