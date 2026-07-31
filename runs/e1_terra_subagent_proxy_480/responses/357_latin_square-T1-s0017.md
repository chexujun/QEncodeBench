```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    qubits = [q for cell in problem_qubits for q in cell] if len(problem_qubits) == 2 else list(problem_qubits)
    target = (1, 0, 0, 0)  # (2,0)=10, (2,2)=00
    for q, bit in zip(qubits, target):
        if bit == 0:
            qc.x(q)
    qc.mcp(3.141592653589793, qubits[:-1], qubits[-1])
    for q, bit in zip(qubits, target):
        if bit == 0:
            qc.x(q)
```
