```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2, q3 = problem_qubits

    # The only vertex cover of size at most 2 is {1, 2}.
    qc.x(q0)
    qc.x(q3)
    qc.h(q3)
    qc.mcx([q0, q1, q2], q3)
    qc.h(q3)
    qc.x(q3)
    qc.x(q0)
```
