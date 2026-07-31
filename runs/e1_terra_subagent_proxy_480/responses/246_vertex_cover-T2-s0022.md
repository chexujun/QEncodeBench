```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    from math import pi

    q = problem_qubits

    qc.x([q[1], q[2], q[3]])
    qc.mcp(pi, [q[0], q[1], q[2], q[3]], q[4])
    qc.x([q[1], q[2], q[3]])

    qc.x([q[0], q[1], q[3]])
    qc.mcp(pi, [q[0], q[1], q[2], q[3]], q[4])
    qc.x([q[0], q[1], q[3]])
```
