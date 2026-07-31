```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    for index in (0, 1, 3, 5):
        qc.x(problem_qubits[index])
    qc.mcx(problem_qubits, ancilla_qubits[0])
    qc.z(ancilla_qubits[0])
    qc.mcx(problem_qubits, ancilla_qubits[0])
    for index in (0, 1, 3, 5):
        qc.x(problem_qubits[index])
```
