```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    for index in (0, 1, 3, 4):
        qc.x(q[index])
    qc.h(q[5])
    qc.mcx(q[:5], q[5])
    qc.h(q[5])
    for index in (0, 1, 3, 4):
        qc.x(q[index])
```
