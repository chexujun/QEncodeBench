```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    for offset in range(5):
        q0, q1, q2, q3 = problem_qubits[offset:offset + 4]
        qc.x(q3)
        qc.h(q3)
        qc.mcx([q0, q1, q2], q3)
        qc.h(q3)
        qc.x(q3)
```
