```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    flags = ancilla_qubits[:4]
    valid = ancilla_qubits[4]

    # Each tuple is (low_a, high_a, low_b, high_b).
    # Toggle target iff the decoded colors of the two endpoints are equal.
    def compute_equal(bits, target):
        # Equal color-0 codes: 00 and 11 are both color 0.
        patterns = (
            (0, 0, 0, 0),
            (0, 0, 1, 1),
            (1, 1, 0, 0),
            (1, 1, 1, 1),
            # Equal color-1 and color-2 codes.
            (1, 0, 1, 0),
            (0, 1, 0, 1),
        )
        for pattern in patterns:
            zero_controls = [q for q, bit in zip(bits, pattern) if bit == 0]
            for q in zero_controls:
                qc.x(q)
            qc.mcx(bits, target)
            for q in reversed(zero_controls):
                qc.x(q)

    edges = ((0, 2), (1, 2), (1, 3), (2, 3))

    for flag, (u, v) in zip(flags, edges):
        compute_equal(
            [
                problem_qubits[2 * u],
                problem_qubits[2 * u + 1],
                problem_qubits[2 * v],
                problem_qubits[2 * v + 1],
            ],
            flag,
        )

    # Valid iff no edge is monochromatic.
    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, valid)
    for flag in reversed(flags):
        qc.x(flag)

    qc.z(valid)

    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, valid)
    for flag in reversed(flags):
        qc.x(flag)

    for flag, (u, v) in reversed(list(zip(flags, edges))):
        compute_equal(
            [
                problem_qubits[2 * u],
                problem_qubits[2 * u + 1],
                problem_qubits[2 * v],
                problem_qubits[2 * v + 1],
            ],
            flag,
        )
```
