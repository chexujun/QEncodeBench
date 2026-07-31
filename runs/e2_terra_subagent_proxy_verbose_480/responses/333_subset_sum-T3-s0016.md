```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    acc = ancilla_qubits[:6]

    def increment_power(control, start_bit, record):
        for target_bit in range(5, start_bit, -1):
            controls = [control] + acc[start_bit:target_bit]
            record.append((controls, acc[target_bit]))
        record.append(([control], acc[start_bit]))

    operations = []
    values = [9, 12, 2, 9, 15]

    for control, value in zip(problem_qubits, values):
        for bit in range(6):
            if (value >> bit) & 1:
                increment_power(control, bit, operations)

    for controls, target in operations:
        if len(controls) == 1:
            qc.cx(controls[0], target)
        else:
            qc.mcx(controls, target)

    # Apply -1 exactly when the six-bit accumulated sum is 26 (0b011010).
    for bit in (0, 2, 5):
        qc.x(acc[bit])
    qc.h(acc[5])
    qc.mcx(acc[:5], acc[5])
    qc.h(acc[5])
    for bit in (5, 2, 0):
        qc.x(acc[bit])

    for controls, target in reversed(operations):
        if len(controls) == 1:
            qc.cx(controls[0], target)
        else:
            qc.mcx(controls, target)
```
