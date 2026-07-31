```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    for qubit in problem_qubits:
        qc.x(qubit)
    qc.mcx(problem_qubits, ancilla_qubits[0])
    for qubit in problem_qubits:
        qc.x(qubit)
```
