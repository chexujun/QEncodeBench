```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2, q3 = problem_qubits

    # Cover {0, 1}: |1100>
    qc.x(q2)
    qc.x(q3)
    qc.h(q3)
    qc.mcx([q0, q1, q2], q3)
    qc.h(q3)
    qc.x(q3)
    qc.x(q2)

    # Cover {1, 3}: |0101>
    qc.x(q0)
    qc.x(q2)
    qc.h(q3)
    qc.mcx([q0, q1, q2], q3)
    qc.h(q3)
    qc.x(q2)
    qc.x(q0)
```
