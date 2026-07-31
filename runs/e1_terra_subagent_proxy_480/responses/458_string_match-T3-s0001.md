```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    for mask in range(1, 1 << 6):
        involved = set()
        for start in range(6):
            if mask & (1 << start):
                involved.update((start, start + 1, start + 2))
        qubits = [problem_qubits[i] for i in sorted(involved)]
        if len(qubits) == 1:
            qc.z(qubits[0])
        else:
            qc.mcp(3.141592653589793, qubits[:-1], qubits[-1])
```
