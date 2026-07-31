```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    target = ancilla_qubits[0]
    zero_controls = [problem_qubits[1], problem_qubits[3], problem_qubits[4]]

    for qubit in zero_controls:
        qc.x(qubit)

    qc.mcx(problem_qubits, target)

    for qubit in reversed(zero_controls):
        qc.x(qubit)
```
