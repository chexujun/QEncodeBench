```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    values = (15, 5, 10, 4, 2)
    sum_qubits = ancilla_qubits[:6]

    def controlled_increment(control, start):
        for j in range(5, start, -1):
            qc.mcx([control] + sum_qubits[start:j], sum_qubits[j])
        qc.cx(control, sum_qubits[start])

    def controlled_decrement(control, start):
        qc.cx(control, sum_qubits[start])
        for j in range(start + 1, 6):
            qc.mcx([control] + sum_qubits[start:j], sum_qubits[j])

    # Compute the selected-element sum in the six-qubit ancilla register.
    for control, value in zip(problem_qubits, values):
        for bit in range(6):
            if (value >> bit) & 1:
                controlled_increment(control, bit)

    # Apply a phase exactly when the sum register contains 10 (binary 001010).
    target = 10
    for bit, qubit in enumerate(sum_qubits):
        if ((target >> bit) & 1) == 0:
            qc.x(qubit)

    qc.h(sum_qubits[5])
    qc.mcx(sum_qubits[:5], sum_qubits[5])
    qc.h(sum_qubits[5])

    for bit, qubit in enumerate(sum_qubits):
        if ((target >> bit) & 1) == 0:
            qc.x(qubit)

    # Uncompute the sum register.
    for control, value in reversed(list(zip(problem_qubits, values))):
        for bit in range(5, -1, -1):
            if (value >> bit) & 1:
                controlled_decrement(control, bit)
```
