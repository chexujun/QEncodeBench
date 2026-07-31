```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    s = ancilla_qubits[:6]
    values = [13, 4, 9, 15, 4]

    def add_power(control, bit, inverse=False):
        if not inverse:
            for j in range(5, bit, -1):
                qc.mcx([control] + s[bit:j], s[j])
            qc.cx(control, s[bit])
        else:
            qc.cx(control, s[bit])
            for j in range(bit + 1, 6):
                qc.mcx([control] + s[bit:j], s[j])

    operations = []
    for control, value in zip(problem_qubits, values):
        for bit in range(6):
            if (value >> bit) & 1:
                add_power(control, bit)
                operations.append((control, bit))

    # The accumulated sum is 32 exactly when s[5] = 1 and s[0:5] = 0.
    for qubit in s[:5]:
        qc.x(qubit)
    qc.mcp(3.141592653589793, s[:5], s[5])
    for qubit in reversed(s[:5]):
        qc.x(qubit)

    for control, bit in reversed(operations):
        add_power(control, bit, inverse=True)
```
