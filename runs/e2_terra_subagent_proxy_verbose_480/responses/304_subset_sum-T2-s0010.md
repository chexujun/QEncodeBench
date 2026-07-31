```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Five ancillas form a reversible 5-bit accumulator for the subset sum.
    s = ancilla_qubits[:5]

    def controlled_add_power(control, bit):
        """Conditionally add 2**bit to the little-endian accumulator."""
        for target_bit in range(4, bit, -1):
            qc.mcx([control] + s[bit:target_bit], s[target_bit])
        qc.cx(control, s[bit])

    def controlled_add_constant(control, value):
        for bit in range(5):
            if (value >> bit) & 1:
                controlled_add_power(control, bit)

    def controlled_sub_constant(control, value):
        for bit in range(4, -1, -1):
            if (value >> bit) & 1:
                for target_bit in range(bit, 5):
                    if target_bit == bit:
                        qc.cx(control, s[target_bit])
                    else:
                        qc.mcx([control] + s[bit:target_bit], s[target_bit])

    # Compute the selected-element sum.
    for control, value in zip(problem_qubits, (8, 4, 9, 3)):
        controlled_add_constant(control, value)

    # Apply -1 exactly when the accumulator is 20 = 10100 (little-endian).
    for bit in (0, 1, 3):
        qc.x(s[bit])
    qc.h(s[4])
    qc.mcx(s[:4], s[4])
    qc.h(s[4])
    for bit in (3, 1, 0):
        qc.x(s[bit])

    # Uncompute the accumulator.
    for control, value in reversed(list(zip(problem_qubits, (8, 4, 9, 3)))):
        controlled_sub_constant(control, value)
```
