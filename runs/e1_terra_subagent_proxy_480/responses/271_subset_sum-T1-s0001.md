```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    values, target = [5,5,5], 10
    for mask in range(8):
        if sum(values[i] for i in range(3) if (mask>>i)&1) == target:
            for i,q in enumerate(problem_qubits):
                if not ((mask>>i)&1): qc.x(q)
            qc.mcp(3.141592653589793,problem_qubits[:-1],problem_qubits[-1])
            for i,q in enumerate(problem_qubits):
                if not ((mask>>i)&1): qc.x(q)
```
