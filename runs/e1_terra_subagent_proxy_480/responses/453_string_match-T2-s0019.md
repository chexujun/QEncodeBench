```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    q = problem_qubits

    qc.x([q[1], q[3], q[4], q[5]])
    qc.h(q[5])
    qc.mcx([q[0], q[1], q[2], q[3], q[4]], q[5])
    qc.h(q[5])
    qc.x([q[1], q[3], q[4], q[5]])

    qc.x([q[2], q[4], q[5], q[6]])
    qc.h(q[6])
    qc.mcx([q[1], q[2], q[3], q[4], q[5]], q[6])
    qc.h(q[6])
    qc.x([q[2], q[4], q[5], q[6]])
```
