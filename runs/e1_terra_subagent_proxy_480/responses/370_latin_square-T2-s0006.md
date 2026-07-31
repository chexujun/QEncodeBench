```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    for i in (1, 3, 4):
        qc.x(q[i])
    qc.h(q[5])
    qc.mcx(q[:5], q[5], ancilla_qubits=ancilla_qubits[:3], mode="v-chain")
    qc.h(q[5])
    for i in (4, 3, 1):
        qc.x(q[i])
```
