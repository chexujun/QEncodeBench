```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q1 = problem_qubits[1]
    q3 = problem_qubits[3]
    q4 = problem_qubits[4]
    q5 = problem_qubits[5]

    # Convert required zero bits into one-controls.
    qc.x(q1)
    qc.x(q4)
    qc.x(q5)

    # Apply -1 iff q1=q3=q4=q5=1.
    qc.h(q5)
    qc.mcx([q1, q3, q4], q5)
    qc.h(q5)

    qc.x(q5)
    qc.x(q4)
    qc.x(q1)
```
