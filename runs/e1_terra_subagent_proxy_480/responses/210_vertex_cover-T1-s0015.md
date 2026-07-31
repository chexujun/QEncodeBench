```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3 = problem_qubits

    qc.x(q1)
    qc.x(q3)
    qc.mcp(np.pi, [q0, q1, q3], q2)
    qc.x(q3)
    qc.x(q1)

    qc.x(q0)
    qc.x(q3)
    qc.mcp(np.pi, [q0, q1, q3], q2)
    qc.x(q3)
    qc.x(q0)
```
