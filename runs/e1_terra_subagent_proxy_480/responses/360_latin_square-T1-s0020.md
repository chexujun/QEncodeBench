```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    target = ancilla_qubits[0]
    zero_controls = [problem_qubits[0], problem_qubits[2]]
    for qubit in zero_controls:
        qc.x(qubit)
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]], target)
    for qubit in zero_controls:
        qc.x(qubit)
```
