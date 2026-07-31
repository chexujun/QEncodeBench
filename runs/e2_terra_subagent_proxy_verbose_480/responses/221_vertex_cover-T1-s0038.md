```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2, q3 = problem_qubits
    xor_ancilla = ancilla_qubits[0]
    predicate_ancilla = ancilla_qubits[1]

    # For this graph and k=2, a valid cover must satisfy:
    # not x0 AND x1 AND (x2 XOR x3).
    qc.cx(q2, xor_ancilla)
    qc.cx(q3, xor_ancilla)

    qc.x(q0)
    qc.mcx([q0, q1, xor_ancilla], predicate_ancilla)
    qc.z(predicate_ancilla)
    qc.mcx([q0, q1, xor_ancilla], predicate_ancilla)
    qc.x(q0)

    qc.cx(q3, xor_ancilla)
    qc.cx(q2, xor_ancilla)
```
