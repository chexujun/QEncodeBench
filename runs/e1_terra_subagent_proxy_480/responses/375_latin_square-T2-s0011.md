```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    inverted = [problem_qubits[1], problem_qubits[3], problem_qubits[5]]
    for qubit in inverted:
        qc.x(qubit)

    target = problem_qubits[0]
    qc.h(target)
    qc.mcx(problem_qubits[1:], target)
    qc.h(target)

    for qubit in inverted:
        qc.x(qubit)
```
