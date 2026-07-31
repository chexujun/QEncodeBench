```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3 = problem_qubits

    qc.x([q0, q2, q3])
    qc.mcp(3.141592653589793, [q0, q2, q3], q1)
    qc.x([q0, q2, q3])

    qc.x([q0, q1, q2])
    qc.mcp(3.141592653589793, [q0, q1, q2], q3)
    qc.x([q0, q1, q2])
```
