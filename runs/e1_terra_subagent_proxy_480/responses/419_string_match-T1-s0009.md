```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    target = ancilla_qubits[0]
    zero_positions = (1, 2, 4)

    for i in zero_positions:
        qc.x(problem_qubits[i])

    qc.h(target)
    qc.mcx(problem_qubits, target)
    qc.h(target)

    for i in zero_positions:
        qc.x(problem_qubits[i])
```
