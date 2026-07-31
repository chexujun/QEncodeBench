```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, x2, x3 = problem_qubits
    a = ancilla_qubits[0]

    # For covers of size at most 2, the predicate simplifies to:
    # x0 AND (NOT x2) AND (x1 XOR x3).
    qc.cx(x1, a)
    qc.cx(x3, a)

    qc.x(x2)
    qc.mcp(3.141592653589793, [x0, x2], a)
    qc.x(x2)

    qc.cx(x3, a)
    qc.cx(x1, a)
```
