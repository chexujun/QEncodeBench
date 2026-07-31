```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    qubits = list(problem_qubits)
    target_bits = [
        1, 0, 0, 1, 0, 0,
        0, 0, 1, 0, 0, 1,
        0, 1, 0, 0, 1, 0,
    ]
    zero_controls = [q for q, bit in zip(qubits, target_bits) if bit == 0]
    for q in zero_controls:
        qc.x(q)
    qc.mcp(3.141592653589793, qubits[:-1], qubits[-1])
    for q in zero_controls:
        qc.x(q)
    return qc
```
