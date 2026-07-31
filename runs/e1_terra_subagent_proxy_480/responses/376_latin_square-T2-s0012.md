```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3, q4, q5 = problem_qubits
    target = ancilla_qubits[0]

    qc.cx(q2, q3)
    qc.cx(q4, q5)
    qc.x(q1)
    qc.x(q3)
    qc.x(q5)

    qc.mcx([q0, q1, q3, q5], target)
    qc.z(target)
    qc.mcx([q0, q1, q3, q5], target)

    qc.x(q5)
    qc.x(q3)
    qc.x(q1)
    qc.cx(q4, q5)
    qc.cx(q2, q3)
```
