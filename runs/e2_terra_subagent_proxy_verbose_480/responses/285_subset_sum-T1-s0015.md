```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, x2 = problem_qubits
    a = ancilla_qubits[0]

    qc.cx(x0, a)
    qc.cx(x1, a)       # a = x0 XOR x1
    qc.cz(a, x2)       # phase iff a = 1 and x2 = 1
    qc.cx(x1, a)
    qc.cx(x0, a)
```
