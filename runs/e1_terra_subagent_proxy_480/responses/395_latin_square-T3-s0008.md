```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    controls = [problem_qubits[0], problem_qubits[1], problem_qubits[3], problem_qubits[5], problem_qubits[6], problem_qubits[7]]
    for qubit in (problem_qubits[1], problem_qubits[3], problem_qubits[5], problem_qubits[7]):
        qc.x(qubit)
    qc.mcx(controls, ancilla_qubits[0])
    for qubit in (problem_qubits[1], problem_qubits[3], problem_qubits[5], problem_qubits[7]):
        qc.x(qubit)
```
