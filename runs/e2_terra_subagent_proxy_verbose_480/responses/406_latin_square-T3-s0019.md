```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Required decoded values:
    # cell 0 = 1: q0=1, q1=0
    # cell 1 = 0: q2=0 (q3 is don't-care)
    # cell 2 = 1: q4=1, q5=0
    # cell 3 = 0: q6=0 (q7 is don't-care)
    q = problem_qubits

    # Convert zero-controls into one-controls.
    for index in (1, 2, 5, 6):
        qc.x(q[index])

    # Apply a six-qubit controlled phase using q6 as the MCX target.
    qc.h(q[6])
    qc.mcx([q[0], q[1], q[2], q[4], q[5]], q[6])
    qc.h(q[6])

    # Restore the problem register.
    for index in (6, 5, 2, 1):
        qc.x(q[index])
```
