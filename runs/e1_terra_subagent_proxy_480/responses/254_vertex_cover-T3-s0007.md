```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    for mask in (0b011001, 0b111000):
        for i, qubit in enumerate(problem_qubits):
            if not ((mask >> i) & 1): qc.x(qubit)
        qc.mcp(3.141592653589793, problem_qubits[:-1], problem_qubits[-1])
        for i, qubit in enumerate(problem_qubits):
            if not ((mask >> i) & 1): qc.x(qubit)
```
