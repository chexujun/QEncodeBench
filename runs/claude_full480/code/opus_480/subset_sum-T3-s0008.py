from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [4, 10, 10, 3, 14]
    T = 17
    n = len(a)

    # Sum bit-width: sum of all = 41 -> needs 6 bits (0..63)
    sum_bits = 6
    s = ancilla_qubits[:sum_bits]

    # Compute running sum s = sum_i x_i * a_i into the ancilla register
    # using controlled increment-by-constant via a ripple over the register.
    def add_constant(control, c):
        # Add constant c (>=0) into register s, conditioned on `control`,
        # modulo 2^sum_bits (values never exceed 41 so no real overflow).
        # Ripple: for each bit position, add with carry chain built from
        # controlled X / Toffoli using s as the accumulator.
        # Implement via successive controlled additions of powers of two.
        cbits = [(c >> k) & 1 for k in range(sum_bits)]
        # Add each set bit of c at position k: this is adding 2^k.
        for k in range(sum_bits):
            if not cbits[k]:
                continue
            # Add 1 at position k into s, controlled by `control`.
            # Ripple carry from position k upward.
            # For bit j (from top down to k): flip s[j] if all lower
            # involved bits are 1 (carry) and control is 1.
            for j in range(sum_bits - 1, k, -1):
                ctrls = [control] + s[k:j]
                qc.mcx(ctrls, s[j])
            qc.cx(control, s[k])

    for i in range(n):
        add_constant(problem_qubits[i], a[i])

    # Phase: -1 iff s == T. Encode target bits: flip zero-bits, MCZ, unflip.
    tbits = [(T >> k) & 1 for k in range(sum_bits)]
    for k in range(sum_bits):
        if tbits[k] == 0:
            qc.x(s[k])
    qc.h(s[-1])
    qc.mcx(s[:-1], s[-1])
    qc.h(s[-1])
    for k in range(sum_bits):
        if tbits[k] == 0:
            qc.x(s[k])

    # Uncompute the sum (mirror in reverse)
    def sub_constant(control, c):
        cbits = [(c >> k) & 1 for k in range(sum_bits)]
        for k in reversed(range(sum_bits)):
            if not cbits[k]:
                continue
            qc.cx(control, s[k])
            for j in range(k + 1, sum_bits):
                ctrls = [control] + s[k:j]
                qc.mcx(ctrls, s[j])

    for i in reversed(range(n)):
        sub_constant(problem_qubits[i], a[i])
