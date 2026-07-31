```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    p = problem_qubits
    for i in (0, 1, 3, 4, 5, 6, 7): qc.x(p[i])
    qc.h(p[7]); qc.mcx([p[i] for i in range(7)], p[7]); qc.h(p[7])
    for i in (0, 1, 3, 4, 5, 6, 7): qc.x(p[i])
```
