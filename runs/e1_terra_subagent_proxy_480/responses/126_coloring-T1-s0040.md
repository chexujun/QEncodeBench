```python
def build_oracle(qc, problem_qubits, ancilla_qubits) -> None:
    flags = ancilla_qubits[:4]
    phase_qubit = ancilla_qubits[4]

    edges = ((0, 1), (1, 2), (1, 3), (2, 3))

    def compute_equal(a0, a1, b0, b1, target):
        # Convert each color to (low_bit, parity).  Color 0 has parity 0;
        # colors 1 and 2 have parity 1 and are distinguished by low_bit.
        qc.cx(a0, a1)
        qc.cx(b0, b1)

        # Both vertices have color 0.
        qc.x(a1)
        qc.x(b1)
        qc.ccx(a1, b1, target)
        qc.x(b1)
        qc.x(a1)

        # Both have parity 1 and identical low bits (both color 1 or color 2).
        qc.cx(a0, b0)
        qc.x(b0)
        qc.mcx([a1, b1, b0], target)
        qc.x(b0)
        qc.cx(a0, b0)

        qc.cx(b0, b1)
        qc.cx(a0, a1)

    for (u, v), flag in zip(edges, flags):
        compute_equal(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )

    # Mark when no edge has equal endpoint colors.
    for flag in flags:
        qc.x(flag)
    qc.x(phase_qubit)
    qc.h(phase_qubit)
    qc.mcx(flags, phase_qubit)
    qc.h(phase_qubit)
    qc.x(phase_qubit)
    for flag in reversed(flags):
        qc.x(flag)

    for (u, v), flag in reversed(list(zip(edges, flags))):
        compute_equal(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )
```
