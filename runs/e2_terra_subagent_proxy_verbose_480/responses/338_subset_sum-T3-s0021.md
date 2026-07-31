```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    total = ancilla_qubits
    values = [4, 13, 3, 9, 15]

    def controlled_add_power(control, start_bit):
        for bit in range(len(total) - 1, start_bit, -1):
            qc.mcx([control] + total[start_bit:bit], total[bit])
        qc.cx(control, total[start_bit])

    def controlled_sub_power(control, start_bit):
        qc.cx(control, total[start_bit])
        for bit in range(start_bit + 1, len(total)):
            qc.mcx([control] + total[start_bit:bit], total[bit])

    def controlled_add_constant(control, value):
        for bit in range(len(total)):
            if (value >> bit) & 1:
                controlled_add_power(control, bit)

    def controlled_sub_constant(control, value):
        for bit in range(len(total) - 1, -1, -1):
            if (value >> bit) & 1:
                controlled_sub_power(control, bit)

    for qubit, value in zip(problem_qubits, values):
        controlled_add_constant(qubit, value)

    # Target 19 is binary 010011 in little-endian order.
    for bit in (2, 3, 5):
        qc.x(total[bit])
    qc.h(total[5])
    qc.mcx(total[:5], total[5])
    qc.h(total[5])
    for bit in (2, 3, 5):
        qc.x(total[bit])

    for qubit, value in reversed(list(zip(problem_qubits, values))):
        controlled_sub_constant(qubit, value)
```
