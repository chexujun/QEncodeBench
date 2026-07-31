```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, _, _, q4, q5 = problem_qubits
    a0, a1 = ancilla_qubits

    # Convert required zero bits into positive controls.
    qc.x(q1)
    qc.x(q4)
    qc.x(q5)

    # Compute the two halves of the conjunction.
    qc.ccx(q0, q1, a0)
    qc.ccx(q4, q5, a1)

    # Apply -1 precisely when both conjunctions hold.
    qc.cz(a0, a1)

    # Uncompute ancillas.
    qc.ccx(q4, q5, a1)
    qc.ccx(q0, q1, a0)

    qc.x(q5)
    qc.x(q4)
    qc.x(q1)
```
