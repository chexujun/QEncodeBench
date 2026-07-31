```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    for i in (0, 3, 4, 5):
        qc.x(problem_qubits[i])

    target = ancilla_qubits[0]
    qc.h(target)
    qc.mcx(problem_qubits, target)
    qc.h(target)

    for i in (0, 3, 4, 5):
        qc.x(problem_qubits[i])
```
