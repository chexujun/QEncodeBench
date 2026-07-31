```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3, q4, q5 = problem_qubits

    qc.cx(q4, q5)
    qc.x(q1)
    qc.x(q2)
    qc.x(q5)

    qc.h(q4)
    qc.mcx([q0, q1, q2, q3, q5], q4)
    qc.h(q4)

    qc.x(q5)
    qc.x(q2)
    qc.x(q1)
    qc.cx(q4, q5)
```
