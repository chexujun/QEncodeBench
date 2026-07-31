```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q = list(problem_qubits)
    for pattern in ((1, 0, 0, 0), (1, 0, 1, 1)):
        zeros = [qubit for qubit, bit in zip(q, pattern) if bit == 0]
        for qubit in zeros:
            qc.x(qubit)
        qc.mcp(3.141592653589793, q[:-1], q[-1])
        for qubit in reversed(zeros):
            qc.x(qubit)
```
