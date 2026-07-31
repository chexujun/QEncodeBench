```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    target = ancilla_qubits[0]
    for a in ((0, 0), (1, 1)):
        for c in ((0, 0), (1, 1)):
            bits = [a[0], a[1], 0, 1, c[0], c[1], 1, 0]
            zero_controls = [q for q, bit in zip(problem_qubits, bits) if bit == 0]
            for q in zero_controls:
                qc.x(q)
            qc.mcx(problem_qubits, target)
            for q in zero_controls:
                qc.x(q)
```
