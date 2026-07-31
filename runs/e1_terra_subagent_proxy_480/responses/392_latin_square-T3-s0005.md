```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    valid_patterns = [[1, 0, b0, b1, c0, c1, 0, 1] for b0, b1 in ((0, 0), (1, 1)) for c0, c1 in ((0, 0), (1, 1))]
    for pattern in valid_patterns:
        zero_qubits = [q for q, bit in zip(problem_qubits, pattern) if bit == 0]
        for q in zero_qubits: qc.x(q)
        qc.mcp(3.141592653589793, problem_qubits[:-1], problem_qubits[-1])
        for q in zero_qubits: qc.x(q)
```
