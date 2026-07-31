```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    acc = ancilla_qubits[:6]

    def controlled_add_power(control, bit):
        # Add 2**bit to acc iff control is 1, modulo 64.
        # Carries are processed high-to-low so their controls see
        # the pre-addition accumulator bits.
        for upper in range(5, bit, -1):
            qc.mcx([control] + acc[bit:upper], acc[upper])
        qc.cx(control, acc[bit])

    def undo_controlled_add_power(control, bit):
        qc.cx(control, acc[bit])
        for upper in range(bit + 1, 6):
            qc.mcx([control] + acc[bit:upper], acc[upper])

    weights = [3, 4, 5, 14, 13]
    additions = []

    for qubit, weight in zip(problem_qubits, weights):
        for bit in range(6):
            if (weight >> bit) & 1:
                controlled_add_power(qubit, bit)
                additions.append((qubit, bit))

    # Phase-flip iff acc == 21 (binary 010101, little-endian).
    for bit in (1, 3, 5):
        qc.x(acc[bit])
    qc.h(acc[5])
    qc.mcx(acc[:5], acc[5])
    qc.h(acc[5])
    for bit in (5, 3, 1):
        qc.x(acc[bit])

    for qubit, bit in reversed(additions):
        undo_controlled_add_power(qubit, bit)
```
